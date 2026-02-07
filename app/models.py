from pydantic import BaseModel, Field
from typing import List, Optional

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