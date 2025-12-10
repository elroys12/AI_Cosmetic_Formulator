# ml_service/app/security.py

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import get_ml_settings

settings = get_ml_settings()
api_key_header = APIKeyHeader(name=settings.ML_API_KEY_HEADER, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key