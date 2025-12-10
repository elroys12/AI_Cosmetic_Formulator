# app/services/auth_service.py

from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.db.supabase_client import get_supabase_client
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth_schema import UserRegister, UserLogin


class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def register_user(self, user_data: UserRegister) -> dict:
        """Register a new user"""
        try:
            # Check if user already exists
            existing = self.supabase.table("users").select("*").eq("email", user_data.email).execute()
            
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Hash password (now handles 72-byte limit)
            hashed_password = get_password_hash(user_data.password)
            
            # Insert user
            new_user = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table("users").insert(new_user).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            user = response.data[0]
            
            # Create access token
            access_token = create_access_token(data={"sub": user["id"]})
            
            # Return structure matching Postman expectations
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user["id"],  # ✅ Added for Postman compatibility
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "is_active": user["is_active"],
                    "created_at": user["created_at"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, credentials: UserLogin) -> dict:
        """Login user and return JWT token"""
        try:
            # Find user by email
            response = self.supabase.table("users").select("*").eq("email", credentials.email).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user = response.data[0]
            
            # Verify password (now handles 72-byte limit)
            if not verify_password(credentials.password, user["hashed_password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Check if user is active
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )
            
            # Create access token
            access_token = create_access_token(data={"sub": user["id"]})
            
            # Return structure matching Postman expectations
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user["id"],  # ✅ Added for Postman compatibility
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "is_active": user["is_active"],
                    "created_at": user["created_at"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )