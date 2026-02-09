"""
Authentication Endpoints

Handles user authentication, registration, and token management.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.core.security import (
    PasswordManager, TokenManager, security, get_current_user_id, AuditLogger
)
from app.schemas.auth import (
    UserLogin, UserRegister, Token, TokenRefresh, PasswordReset, PasswordChange
)
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.register_user(user_data)
        AuditLogger.log_authentication_attempt(
            user_id=user.id,
            ip_address="unknown",  # Would be extracted from request
            success=True,
            details="User registration successful"
        )
        return user
    except Exception as e:
        AuditLogger.log_authentication_attempt(
            user_id=None,
            ip_address="unknown",
            success=False,
            details=f"Registration failed: {str(e)}"
        )
        raise


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Authenticate user and return access token."""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.authenticate_user(
            user_credentials.email,
            user_credentials.password
        )
        
        if not user:
            AuditLogger.log_authentication_attempt(
                user_id=None,
                ip_address="unknown",
                success=False,
                details="Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        access_token = TokenManager.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        refresh_token = TokenManager.create_refresh_token(
            data={"sub": user.id}
        )
        
        AuditLogger.log_authentication_attempt(
            user_id=user.id,
            ip_address="unknown",
            success=True,
            details="Login successful"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        AuditLogger.log_authentication_attempt(
            user_id=None,
            ip_address="unknown",
            success=False,
            details=f"Login error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = TokenManager.verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user to include in new token
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = TokenManager.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,  # Keep same refresh token
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get current user information."""
    user_id = get_current_user_id(credentials)
    
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Any:
    """Logout user (invalidate token)."""
    user_id = get_current_user_id(credentials)
    
    # In a production system, you would add the token to a blacklist
    # For now, we just log the logout event
    AuditLogger.log_authentication_attempt(
        user_id=user_id,
        ip_address="unknown",
        success=True,
        details="User logout"
    )
    
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Change user password."""
    user_id = get_current_user_id(credentials)
    
    auth_service = AuthService(db)
    
    try:
        await auth_service.change_password(
            user_id,
            password_data.current_password,
            password_data.new_password
        )
        
        AuditLogger.log_security_event(
            "PASSWORD_CHANGE",
            {"user_id": user_id, "success": True}
        )
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        AuditLogger.log_security_event(
            "PASSWORD_CHANGE",
            {"user_id": user_id, "success": False, "error": str(e)}
        )
        raise


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reset user password (would typically send email)."""
    auth_service = AuthService(db)
    
    # In a real implementation, this would:
    # 1. Generate a secure reset token
    # 2. Send email with reset link
    # 3. Store token with expiration
    
    user = await auth_service.get_user_by_email(reset_data.email)
    
    if user:
        AuditLogger.log_security_event(
            "PASSWORD_RESET_REQUEST",
            {"user_id": user.id, "email": reset_data.email}
        )
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}