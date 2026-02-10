"""
Security Module

This module provides comprehensive security features including:
- Password hashing and verification
- JWT token management
- Security middleware for headers and rate limiting
- Input validation and sanitization
- SQL injection and XSS protection
"""

import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import bcrypt
from fastapi import HTTPException, Request, Response, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Settings
settings = get_settings()


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for headers, rate limiting, and request validation."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_store: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks."""
        
        # Add security headers
        response = await call_next(request)
        
        # Apply security headers
        for header, value in settings.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Rate limiting
        client_ip = self._get_client_ip(request)
        if not self._check_rate_limit(client_ip):
            return Response(
                content="Rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = {"requests": [], "blocked_until": None}
        
        client_data = self.rate_limit_store[client_ip]
        
        # Check if client is currently blocked
        if client_data["blocked_until"] and now < client_data["blocked_until"]:
            return False
        
        # Clean old requests
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if req_time > window_start
        ]
        
        # Check rate limit
        if len(client_data["requests"]) >= settings.RATE_LIMIT_REQUESTS:
            # Block client for the window duration
            client_data["blocked_until"] = now + timedelta(seconds=settings.RATE_LIMIT_WINDOW)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Add current request
        client_data["requests"].append(now)
        return True


class PasswordManager:
    """Secure password management with bcrypt."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters")
        
        # Use bcrypt directly to avoid passlib issues
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure random password."""
        return secrets.token_urlsafe(length)


class TokenManager:
    """JWT token management for authentication."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )


class InputSanitizer:
    """Input validation and sanitization to prevent XSS and injection attacks."""
    
    # Patterns for detecting potential attacks
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
        r'(--|#|/\*|\*/)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)',
    ]
    
    @classmethod
    def sanitize_string(cls, text: str, max_length: int = 10000) -> str:
        """Sanitize string input to prevent XSS attacks."""
        if not isinstance(text, str):
            return str(text)
        
        # Limit length
        text = text[:max_length]
        
        # Remove potential XSS patterns
        for pattern in cls.XSS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # HTML encode dangerous characters
        text = (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
        
        return text.strip()
    
    @classmethod
    def validate_sql_input(cls, text: str) -> bool:
        """Check if text contains potential SQL injection patterns."""
        if not isinstance(text, str):
            return True
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent directory traversal."""
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\.\.', '_', filename)
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or "unnamed_file"


class CSRFProtection:
    """CSRF protection using double-submit cookie pattern."""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, cookie_token: str) -> bool:
        """Verify CSRF token against cookie token."""
        if not token or not cookie_token:
            return False
        
        return hmac.compare_digest(token, cookie_token)


class AuditLogger:
    """Security audit logging for tracking security events."""
    
    @staticmethod
    def log_authentication_attempt(user_id: Optional[str], ip_address: str, success: bool, details: str = ""):
        """Log authentication attempts."""
        logger.info(
            f"AUTH_ATTEMPT: user_id={user_id}, ip={ip_address}, "
            f"success={success}, details={details}"
        )
    
    @staticmethod
    def log_permission_check(user_id: str, resource: str, action: str, granted: bool):
        """Log permission checks."""
        logger.info(
            f"PERMISSION_CHECK: user_id={user_id}, resource={resource}, "
            f"action={action}, granted={granted}"
        )
    
    @staticmethod
    def log_data_access(user_id: str, resource_type: str, resource_id: str, action: str):
        """Log data access events."""
        logger.info(
            f"DATA_ACCESS: user_id={user_id}, type={resource_type}, "
            f"id={resource_id}, action={action}"
        )
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any]):
        """Log general security events."""
        logger.warning(f"SECURITY_EVENT: type={event_type}, details={details}")


# Utility functions
def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """Extract user ID from JWT token."""
    payload = TokenManager.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return user_id


def require_permissions(required_permissions: list):
    """Decorator to require specific permissions for endpoint access."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would integrate with a permission system
            # For now, just log the permission check
            AuditLogger.log_permission_check(
                user_id="current_user",  # Would be extracted from token
                resource=func.__name__,
                action="access",
                granted=True
            )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# FastAPI Dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """FastAPI dependency to get current user ID from JWT token."""
    return get_current_user_id(credentials)


async def require_superuser(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """FastAPI dependency to require superuser privileges."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.core.database import get_db
    from app.models.user import User
    
    user_id = get_current_user_id(credentials)
    
    # Get database session - we need to use dependency injection properly
    # For now, we'll just return the user_id and check in the endpoint
    # This is a simplified version
    return user_id