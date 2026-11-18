
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


# Schema for creating a new user
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# Schema for returning user details
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Schema for updating user details
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = ConfigDict(from_attributes=True)
