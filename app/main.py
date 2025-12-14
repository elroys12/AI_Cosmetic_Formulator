from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import os

from app.config.settings import get_settings
from app.routers import auth, analyze, history
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 STARTING {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 Debug mode: {settings.DEBUG}")
    logger.info(f"🔗 ML Service URL: {settings.ML_MODEL_URL}")
    logger.info(f"🌐 Port: {os.getenv('PORT', '8000')}")
    logger.info(f"🎯 Environment: {'production' if not settings.DEBUG else 'development'}")
    
    yield
    
    logger.info(f"🛑 SHUTTING DOWN {settings.APP_NAME}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Novel Chemicals Discovery Agent",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ✅ CRITICAL FIX: Add /api prefix when including routers
app.include_router(auth.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(history.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "success": True,
        "message": "Novel Chemicals Discovery API is running",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "ml_service": settings.ML_MODEL_URL,
        "environment": "production" if not settings.DEBUG else "development"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ml_service_url": settings.ML_MODEL_URL,
        "environment": "production" if not settings.DEBUG else "development"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)