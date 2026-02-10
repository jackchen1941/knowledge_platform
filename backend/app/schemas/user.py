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
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False


class UserUpdate(BaseModel):
    """User update schema."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema."""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserProfile(UserResponse):
    """Extended user profile schema."""
    knowledge_items_count: int = 0
    categories_count: int = 0
    tags_count: int = 0