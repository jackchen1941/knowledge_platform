"""
Authentication Service

Business logic for user authentication and management.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.security import PasswordManager, InputSanitizer
from app.core.exceptions import ValidationError, AuthenticationError, ConflictError
from app.models.user import User
from app.schemas.auth import UserRegister


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user."""
        
        # Sanitize inputs
        username = InputSanitizer.sanitize_string(user_data.username, 50)
        email = user_data.email.lower().strip()
        full_name = InputSanitizer.sanitize_string(user_data.full_name or "", 100)
        
        # Validate SQL injection patterns
        if not InputSanitizer.validate_sql_input(username):
            raise ValidationError("Invalid username format")
        
        # Check if user already exists
        existing_user = await self._get_user_by_email_or_username(email, username)
        if existing_user:
            if existing_user.email == email:
                raise ConflictError("Email already registered")
            if existing_user.username == username:
                raise ConflictError("Username already taken")
        
        # Hash password
        password_hash = PasswordManager.hash_password(user_data.password)
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name if full_name else None,
            is_active=True,
            is_verified=False,
            preferences={}
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"New user registered: {user.id} ({user.email})")
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        
        # Sanitize email
        email = email.lower().strip()
        
        # Get user by email
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        
        # Verify password
        if not PasswordManager.verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        
        # Get user
        user = await self.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        # Verify current password
        if not PasswordManager.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = PasswordManager.hash_password(new_password)
        
        # Update password
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Password changed for user: {user.id}")
        return True
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account."""
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"User deactivated: {user.id}")
        return True
    
    async def _get_user_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        """Get user by email or username."""
        result = await self.db.execute(
            select(User).where(
                (User.email == email) | (User.username == username)
            )
        )
        return result.scalar_one_or_none()