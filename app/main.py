# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Novel Chemicals Discovery Agent",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration - FIXED
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # ✅ Use property
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include Routers
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)


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


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"ML Service URL: {settings.ML_MODEL_URL}")
    logger.info(f"Port: {os.getenv('PORT', '8000')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    # Use Railway PORT environment variable
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )