# ml_service/app/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Literal, Optional
import json


class MLServiceSettings(BaseSettings):
    # App Config
    APP_NAME: str = "Novel Chemical ML Service"
    APP_VERSION: str = "1.0.0-hybrid"
    DEBUG: bool = False
    
    # Security
    API_KEY: str
    ML_API_KEY_HEADER: str = "X-API-Key"
    
    # Google Gemini (Fallback + Embedding)
    GEMINI_API_KEY: str
    GOOGLE_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Groq AI (Primary LLM) - Optional with defaults
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Hybrid Configuration - Optional with defaults
    PRIMARY_LLM_PROVIDER: Literal["groq", "gemini"] = "gemini"  # Default to gemini
    FALLBACK_ENABLED: bool = True
    
    # Data Paths
    DATA_DIR: str = "data"
    
    # CORS
    ALLOWED_ORIGINS: str = '["*"]'
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert ALLOWED_ORIGINS to list"""
        if not self.ALLOWED_ORIGINS:
            return ["*"]
        
        origins = self.ALLOWED_ORIGINS
        
        # Jika berupa JSON array string
        if origins.strip().startswith("["):
            try:
                return json.loads(origins)
            except:
                # Fallback ke comma-separated
                pass
        
        # Jika comma-separated
        return [
            origin.strip() 
            for origin in origins.split(",")
            if origin.strip()
        ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'


@lru_cache()
def get_ml_settings() -> MLServiceSettings:
    """Get cached settings instance"""
    return MLServiceSettings()