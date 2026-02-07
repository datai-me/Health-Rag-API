from datetime import datetime, timedelta
from typing import Optional
import bcrypt  # Import direct de Bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, TokenData
from app.config import get_settings

settings = get_settings()

# Configuration de la sécurité
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Schéma OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe avec bcrypt direct.
    On découpe [:72] car bcrypt a une stricte limite de 72 octets.
    """
    # Attention : Bcrypt attend des bytes, pas des strings
    password_bytes = plain_password[:72].encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt direct.
    """
    # Génération du sel (salt) et hashage
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # On retourne un string pour le stocker en base
    return hashed_bytes.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Génère le JWT (inchangé)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, username: str):
    """Récupère l'utilisateur (inchangé)"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authentifie l'utilisateur (inchangé, utilise les nouvelles fonctions bcrypt ci-dessus)"""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Vérifie le token JWT (inchangé)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user