from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
# Modèle pour la Base de Données (SQLAlchemy) - Importé dans database.py
from sqlalchemy import Column, Integer, String
from app.database import Base
# Pour les validations
from pydantic import BaseModel, Field, field_validator
import re


# --- MODÈLES RAG ---

class IngestRequest(BaseModel):
    """
    Modèle de requête pour l'endpoint d'ingestion.
    Définit la structure attendue lors de l'ajout de nouvelles données médicales.
    """
    drug_name: str = Field(
        ...,
        description="Le nom commercial ou générique du médicament à rechercher (ex: 'aspirin', 'ibuprofen').",
        example="aspirin",
        min_length=2
    )

class AskRequest(BaseModel):
    """
    Modèle de requête pour l'endpoint de question/réponse.
    Définit la structure de la question posée par l'utilisateur.
    """
    question: str = Field(
        ...,
        description="La question en langage naturel concernant les médicaments ingérés.",
        example="Quels sont les effets secondaires de l'aspirine ?",
        min_length=5
    )

class SourceInfo(BaseModel):
    """
    Modèle représentant un extrait de source utilisé pour générer la réponse.
    """
    content_preview: str = Field(
        ...,
        description="Un extrait court du texte source utilisé pour formuler la réponse."
    )
    source_type: str = Field(
        default="OpenFDA",
        description="L'origine des données (actuellement OpenFDA)."
    )

class AnswerResponse(BaseModel):
    """
    Modèle de réponse retourné par l'endpoint /ask.
    Contient la réponse générée par l'IA et ses sources.
    """
    answer: str = Field(
        ...,
        description="La réponse générée par le modèle de langage (LLM)."
    )
    sources: List[SourceInfo] = Field(
        default_factory=list,
        description="Liste des fragments de texte ayant servi de contexte à la réponse."
    )

# --- MODÈLES AUTHENTIFICATION (DB & API) ---

class User(Base):
    """
    Table des utilisateurs dans la base SQLite.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Modèles pour l'API (Pydantic)
class UserLogin(BaseModel):
    """Données nécessaires pour se connecter."""
    username: str = Field(..., min_length=1, example="johndoe")
    password: str = Field(..., min_length=1, example="SecureP@ss1")

class Token(BaseModel):
    """Réponse lors d'une connexion réussie."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Structure interne du payload JWT."""
    username: Optional[str] = None

class UserCreate(BaseModel):
    """Données nécessaires pour créer un utilisateur."""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        description="Le nom d'utilisateur (entre 3 et 20 caractères)", 
        example="johndoe"
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.", 
        example="SecureP@ss1"
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valide que le mot de passe respecte les règles de sécurité :
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule.')
        if not re.search(r"[a-z]", v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule.')
        if not re.search(r"[0-9]", v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre.')
        if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial.')
        return v

