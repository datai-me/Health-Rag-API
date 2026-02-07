from pydantic_settings import BaseSettings

from functools import lru_cache

class Settings(BaseSettings):
    """Classe de configuration chargée depuis le fichier .env"""
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance unique des paramètres."""
    return Settings()