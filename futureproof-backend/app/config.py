# import os
# from typing import List
# from pydantic import ConfigDict
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     """Application settings from environment variables"""
    
#     # Add model_config to allow extra fields from .env
#     model_config = ConfigDict(
#         extra='ignore',
#         env_file='.env',
#         env_file_encoding='utf-8',
#         case_sensitive=False
#     )
    
#     # Application
#     APP_NAME: str = "FutureProof"
#     DEBUG: bool = True
#     SECRET_KEY: str = "your-secret-key-here-change-in-production"
#     API_V1_STR: str = "/api/v1"  # ← THIS WAS MISSING!
    
#     # Database - construct from individual parts
#     POSTGRES_USER: str = "postgres"
#     POSTGRES_PASSWORD: str = "postgres"
#     POSTGRES_HOST: str = "postgres"
#     POSTGRES_PORT: str = "5432"
#     POSTGRES_DB: str = "futureproof_db"
    
#     # Redis
#     REDIS_URL: str = "redis://redis:6379/0"
    
#     # API Keys
#     GROQ_API_KEY: str = ""
#     CLINE_API_KEY: str = ""
#     GITHUB_TOKEN: str = ""
#     CODERABBIT_API_KEY: str = ""
#     HUGGINGFACE_TOKEN: str = ""
    
#     # Services
#     KESTRA_API_URL: str = "http://kestra:8080"
    
#     # Oumi
#     OUMI_MODEL_PATH: str = "./models/oumi-finetuned"
    
#     # CORS
#     CORS_ORIGINS: List[str] = [
#         "http://localhost:3000",
#         "http://localhost:8000",
#         "http://localhost:8080"
#     ]
    
#     @property
#     def DATABASE_URL(self) -> str:
#         """Construct database URL from components"""
#         return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# # Instantiate settings
# settings = Settings()


"""
Application Configuration
Loads environment variables and provides settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://futureproof:futureproof123@db:5432/futureproof"
    
    # API Keys
    GROQ_API_KEY: str
    GITHUB_TOKEN: Optional[str] = None
    OUMI_API_KEY: Optional[str] = None
    CODERABBIT_API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Frontend URL (for CORS)
    FRONTEND_URL: Optional[str] = None  # e.g., https://your-app.vercel.app
    
    # App Settings
    APP_NAME: str = "FutureProof"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Transformation Settings
    MAX_FILES_TO_TRANSFORM: int = 20  # Limit files per transformation
    TRANSFORMATION_TIMEOUT: int = 300  # 5 minutes timeout
    
    # Analysis Settings
    MAX_ISSUES_PER_CATEGORY: int = 100
    ANALYSIS_TIMEOUT: int = 600  # 10 minutes
    
    # Rate Limiting (future use)
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
