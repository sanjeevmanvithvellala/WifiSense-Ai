"""
Application Configuration and Settings for WiFiSense AI Backend.
"""

from typing import List
import os
import json
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "WiFiSense AI")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wifisense.db")

    # Paths
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    MODELS_DIR: str = os.getenv("MODELS_DIR", "./models/registry")

    # Streaming & Replay
    DEFAULT_REPLAY_SAMPLE_RATE_HZ: float = float(os.getenv("DEFAULT_REPLAY_SAMPLE_RATE_HZ", "50.0"))
    MAX_BUFFER_SIZE: int = int(os.getenv("MAX_BUFFER_SIZE", "1000"))


settings = Settings()
