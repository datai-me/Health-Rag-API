from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# --- Imports des modèles DB & Auth ---
from app.database import get_db
from app.models import (
    User, 
    UserCreate, 
    UserLogin, 
    Token,
    # --- Imports des modèles RAG ---
    IngestRequest, 
    AskRequest, 
    AnswerResponse, 
    SourceInfo
)

from app.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

# --- Imports des Services ---
from app.services.fda_service import FDAService
from app.services.rag_service import RAGService

# Initialisation des services
fda_service = FDAService()
rag_service = RAGService()
router = APIRouter()

# --- ROUTES D'AUTHENTIFICATION ---

@router.post("/auth/register", status_code=status.HTTP_201_CREATED, summary="Inscription")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un utilisateur.
    
    Validations effectuées :
    1. Format (Automatique Pydantic): Longueur, regex mot de passe -> Code 422.
    2. Métier (Code ci-dessous): Si l'utilisateur existe déjà -> Code 400.
    """
    
    # VALIDATION MÉTIER : Vérifier si l'utilisateur existe déjà
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ce nom d'utilisateur est déjà pris."
        )

    # Si tout est bon, on crée l'utilisateur
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # On renvoie le token immédiatement
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "message": "Compte créé avec succès"}

@router.post("/auth/login", status_code=status.HTTP_200_OK, summary="Connexion (Login)")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur.
    
    Validations effectuées :
    1. Format (Automatique Pydantic): Longueur -> Code 422.
    2. Métier (Code ci-dessous): 
       - Si l'utilisateur n'existe pas -> Code 401.
       - Si le mot de passe est faux -> Code 401.
    """
    
    # VALIDATION MÉTIER : Tentative d'authentification
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nom d'utilisateur ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Si authentification réussie, génération du token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/logout", summary="Déconnexion (Logout)")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Déconnexion réussie."}


# --- ROUTES RAG (PROTÉGÉES) ---

@router.post("/ingest", summary="Ingestion de médicament", tags=["RAG Operations"])
async def ingest_data(
    req: IngestRequest, 
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint sécurisé pour ingérer des données.
    Nécessite d'être connecté via JWT.
    """
    raw = fda_service.fetch_drug_data(req.drug_name)
    if not raw:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    
    texts = fda_service.clean_and_format_data(raw)
    count = rag_service.ingest_documents(texts)
    return {"message": f"Ingestion OK par {current_user.username}", "chunks": count}

@router.post("/ask", response_model=AnswerResponse, summary="Poser une question", tags=["RAG Operations"])
async def ask_question(
    req: AskRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint sécurisé pour poser une question.
    Nécessite d'être connecté via JWT.
    """
    answer, raw_sources = rag_service.query(req.question)
    sources = [SourceInfo(content_preview=s) for s in raw_sources]
    return AnswerResponse(answer=answer, sources=sources)