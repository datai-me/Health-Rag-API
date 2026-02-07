"""
Application configuration using Pydantic Settings.
All settings are loaded from environment variables.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="Health RAG API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite:///./health_rag.db",
        description="Database connection URL"
    )
    
    # Security / JWT
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT encoding (must be at least 32 characters)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="JWT access token expiration (in minutes)"
    )
    
    # External APIs
    groq_api_key: str = Field(default="", description="Groq API key")
    jina_api_key: str = Field(default="", description="Jina embeddings API key")
    openai_api_key: str = Field(default="", description="OpenAI API key (optional)")
    
    # FDA Service
    fda_api_base_url: str = Field(
        default="https://api.fda.gov/drug/label.json",
        description="OpenFDA API base URL"
    )
    fda_request_timeout: int = Field(default=10, description="FDA API request timeout in seconds")
    fda_max_results: int = Field(default=3, ge=1, le=100, description="Maximum results from FDA API")
    
    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, ge=100, le=5000, description="Text chunk size for RAG")
    rag_chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Chunk overlap size")
    rag_top_k_results: int = Field(default=3, ge=1, le=20, description="Top K results for retrieval")
    rag_llm_model: str = Field(default="llama-3.3-70b-versatile", description="LLM model name")
    rag_llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="LLM temperature")
    rag_embedding_model: str = Field(
        default="jina-embeddings-v2-base-en",
        description="Embedding model name"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins if provided as string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded only once
    and reused across the application.
    """
    return Settings()
