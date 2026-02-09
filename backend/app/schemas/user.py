"""
User Schemas

Pydantic models for user-related requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """User response schema."""
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile schema."""
    knowledge_items_count: int = 0
    categories_count: int = 0
    tags_count: int = 0