from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Raiox AI"
    PROJECT_VERSION: str = "2.0.0"
    PROJECT_DESCRIPTION: str = "API para processamento de imagens de raio-X com CLIP"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "raiox_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "Xc7!rA2v9Z@1pQ3y")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "raiox_db")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # DigitalOcean Spaces
    DO_SPACES_KEY: str = os.getenv("DO_SPACES_KEY", "DO00CVCTFVXPANB4DD9M")
    DO_SPACES_SECRET: str = os.getenv("DO_SPACES_SECRET", "+nWSRpFnQ+MncvZKDdw/herwYQRo0YEvVHujg1YMmaA")
    DO_SPACES_BUCKET: str = os.getenv("DO_SPACES_BUCKET", "raiox-imagens")
    DO_SPACES_REGION: str = os.getenv("DO_SPACES_REGION", "nyc3")
    DO_SPACES_ENDPOINT: str = os.getenv("DO_SPACES_ENDPOINT", "https://nyc3.digitaloceanspaces.com")
    
    # CLIP Model
    CLIP_MODEL: str = os.getenv("CLIP_MODEL", "ViT-B/32")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"


settings = Settings()
