from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    app_name: str = "Robotics Textbook API"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str
    
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    
    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4-turbo"
    
    # Auth
    better_auth_secret: str
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Redis (optional)
    redis_url: Optional[str] = None
    
    # Sentry (optional)
    sentry_dsn: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Derived values
CORS_ORIGINS = [url.strip() for url in settings.cors_origins.split(",")]
EMBEDDING_MODEL = settings.openai_embedding_model
CHAT_MODEL = settings.openai_chat_model
