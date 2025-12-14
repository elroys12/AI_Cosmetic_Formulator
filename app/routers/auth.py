from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schema import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.utils.logger import get_logger

# ✅ CORRECT: No /api prefix
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

logger = get_logger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: 8-72 characters with uppercase, lowercase, and number
    - **full_name**: User's full name (2-100 characters)
    """
    try:
        auth_service = AuthService()
        result = await auth_service.register_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login user and get JWT token
    
    - **email**: Registered email
    - **password**: User password (max 72 characters)
    """
    try:
        auth_service = AuthService()
        result = await auth_service.login_user(credentials)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )