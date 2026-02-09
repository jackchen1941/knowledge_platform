"""
Authentication Schemas

Pydantic models for authentication-related requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

from app.core.config import get_settings

settings = get_settings()


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    """User registration request schema."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {settings.PASSWORD_MIN_LENGTH} characters')
        
        # Check for at least one digit and one letter
        has_digit = any(c.isdigit() for c in v)
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('Password must contain at least one letter and one digit')
        
        return v


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change request schema."""
    current_password: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {settings.PASSWORD_MIN_LENGTH} characters')
        
        has_digit = any(c.isdigit() for c in v)
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('Password must contain at least one letter and one digit')
        
        return v


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr