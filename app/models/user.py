# app/models/user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None