# app/config/settings.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Novel Chemicals Discovery API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # ML Model
    ML_MODEL_URL: str
    ML_MODEL_TIMEOUT: int = 30
    ML_API_KEY: str
    
    # CORS - Support multiple formats
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
                import json
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


@lru_cache()
def get_settings() -> Settings:
    return Settings()