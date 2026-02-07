from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # --- CLÉS API (IA) ---
    groq_api_key: str = ""
    jina_api_key: str = ""
    openai_api_key: str = ""
    
    # --- CONFIGURATION SÉCURITÉ (JWT) ---
    # Aucune valeur par défaut : L'app crashera si la clé n'est pas dans le .env (Sécurité accrue)
    secret_key: str 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()