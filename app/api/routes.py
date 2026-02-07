from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# Imports DB & Auth
from app.database import get_db
from app.models import User, UserCreate, UserLogin, Token
from app.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

# Imports RAG
from app.models import IngestRequest, AskRequest, AnswerResponse, SourceInfo
from app.services.fda_service import FDAService
from app.services.rag_service import RAGService

# Initialisation des services
fda_service = FDAService()
rag_service = RAGService()
router = APIRouter()

# --- ROUTES D'AUTHENTIFICATION ---

@router.post("/auth/register", response_model=Token, summary="Inscription")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel utilisateur dans la base de données et renvoie un token d'accès immédiatement.
    """
    # Vérifier si l'utilisateur existe déjà
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")

    # Créer le nouvel utilisateur avec mot de passé hashé
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Générer le token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/login", response_model=Token, summary="Connexion (Login)")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion standard OAuth2.
    Dans Swagger UI, cliquez sur le cadenas 🔒 en haut à droite.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/logout", summary="Déconnexion (Logout)")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Déconnexion client. 
    Note : Comme les JWT sont stateless, le "logout" côté serveur est complexe 
    (nécessite une blacklist). Ici, nous confirmons simplement que l'utilisateur peut supprimer son token côté client.
    """
    return {"message": "Déconnexion réussie. Veuillez supprimer votre token client."}


# --- ROUTES RAG (PROTÉGÉES) ---

@router.post("/ingest", summary="Ingestion de médicament", tags=["RAG Operations"])
async def ingest_data(
    req: IngestRequest, 
    current_user: User = Depends(get_current_user) # <--- PROTECTION ICI
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
    current_user: User = Depends(get_current_user) # <--- PROTECTION ICI
):
    """
    Endpoint sécurisé pour poser une question.
    Nécessite d'être connecté via JWT.
    """
    answer, raw_sources = rag_service.query(req.question)
    sources = [SourceInfo(content_preview=s) for s in raw_sources]
    return AnswerResponse(answer=answer, sources=sources)