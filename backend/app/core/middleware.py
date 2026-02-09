"""
Middleware Components

Custom middleware for authentication, authorization, and security.
"""

from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenManager, AuditLogger
from app.services.permission import PermissionService
from app.services.auth import AuthService


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT token authentication."""
    
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through authentication."""
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return Response(
                content="Missing or invalid authorization header",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        token = authorization.split(" ")[1]
        
        try:
            # Verify token
            payload = TokenManager.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Add user info to request state
            request.state.user_id = user_id
            request.state.token_payload = payload
            
            # Continue with request
            response = await call_next(request)
            return response
            
        except Exception as e:
            AuditLogger.log_authentication_attempt(
                user_id=None,
                ip_address=self._get_client_ip(request),
                success=False,
                details=f"Token verification failed: {str(e)}"
            )
            
            return Response(
                content="Invalid or expired token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (doesn't require authentication)."""
        public_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/reset-password",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


def require_permission(permission_name: str):
    """Decorator to require specific permission for endpoint access."""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args (FastAPI dependency injection)
            request = None
            db = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, AsyncSession):
                    db = arg
            
            # Get from kwargs if not in args
            if not request:
                request = kwargs.get('request')
            if not db:
                db = kwargs.get('db')
            
            if not request or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing request or database session"
                )
            
            # Get user ID from request state (set by AuthenticationMiddleware)
            user_id = getattr(request.state, 'user_id', None)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            permission_service = PermissionService(db)
            has_permission = await permission_service.check_user_permission(
                user_id, permission_name
            )
            
            if not has_permission:
                AuditLogger.log_permission_check(
                    user_id, "endpoint", func.__name__, False
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {permission_name} required"
                )
            
            AuditLogger.log_permission_check(
                user_id, "endpoint", func.__name__, True
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(role_name: str):
    """Decorator to require specific role for endpoint access."""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and db from args/kwargs
            request = None
            db = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, AsyncSession):
                    db = arg
            
            if not request:
                request = kwargs.get('request')
            if not db:
                db = kwargs.get('db')
            
            if not request or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing request or database session"
                )
            
            # Get user ID from request state
            user_id = getattr(request.state, 'user_id', None)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has the required role
            permission_service = PermissionService(db)
            user_roles = await permission_service.get_user_roles(user_id)
            
            has_role = any(role.name == role_name for role in user_roles)
            
            if not has_role:
                AuditLogger.log_permission_check(
                    user_id, "role", role_name, False
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_name}"
                )
            
            AuditLogger.log_permission_check(
                user_id, "role", role_name, True
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def get_current_user(request: Request, db: AsyncSession = None) -> Optional[str]:
    """Get current authenticated user ID from request."""
    return getattr(request.state, 'user_id', None)


async def get_current_user_with_permissions(request: Request, db: AsyncSession) -> tuple:
    """Get current user ID and their permissions."""
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        return None, set()
    
    permission_service = PermissionService(db)
    permissions = await permission_service.get_user_permissions(user_id)
    
    return user_id, permissions


class PermissionCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic permission checking based on endpoint patterns."""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Define permission mappings for different endpoint patterns
        self.endpoint_permissions = {
            # Knowledge management
            "POST /api/v1/knowledge": "knowledge.create",
            "GET /api/v1/knowledge": "knowledge.read",
            "PUT /api/v1/knowledge": "knowledge.update",
            "DELETE /api/v1/knowledge": "knowledge.delete",
            
            # Category management
            "POST /api/v1/categories": "category.create",
            "GET /api/v1/categories": "category.read",
            "PUT /api/v1/categories": "category.update",
            "DELETE /api/v1/categories": "category.delete",
            
            # Tag management
            "POST /api/v1/tags": "tag.create",
            "GET /api/v1/tags": "tag.read",
            "PUT /api/v1/tags": "tag.update",
            "DELETE /api/v1/tags": "tag.delete",
            
            # User management
            "GET /api/v1/users": "user.read",
            "PUT /api/v1/users": "user.update",
            "DELETE /api/v1/users": "user.delete",
            
            # System administration
            "GET /api/v1/permissions": "system.admin",
            "POST /api/v1/permissions": "system.admin",
            "PUT /api/v1/permissions": "system.admin",
            "DELETE /api/v1/permissions": "system.admin",
            
            "GET /api/v1/roles": "system.admin",
            "POST /api/v1/roles": "system.admin",
            "PUT /api/v1/roles": "system.admin",
            "DELETE /api/v1/roles": "system.admin",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through permission checking."""
        
        # Skip for public endpoints or if no user authenticated
        user_id = getattr(request.state, 'user_id', None)
        if not user_id or self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Check if endpoint requires specific permission
        endpoint_key = f"{request.method} {request.url.path}"
        required_permission = self._get_required_permission(endpoint_key)
        
        if required_permission:
            # Get database session
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                permission_service = PermissionService(db)
                has_permission = await permission_service.check_user_permission(
                    user_id, required_permission
                )
                
                if not has_permission:
                    AuditLogger.log_permission_check(
                        user_id, "endpoint", request.url.path, False
                    )
                    return Response(
                        content=f"Insufficient permissions: {required_permission} required",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                
                AuditLogger.log_permission_check(
                    user_id, "endpoint", request.url.path, True
                )
                
            finally:
                await db.close()
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public."""
        public_paths = [
            "/api/v1/auth/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _get_required_permission(self, endpoint_key: str) -> Optional[str]:
        """Get required permission for endpoint."""
        # Direct match
        if endpoint_key in self.endpoint_permissions:
            return self.endpoint_permissions[endpoint_key]
        
        # Pattern matching for dynamic routes
        for pattern, permission in self.endpoint_permissions.items():
            if self._matches_pattern(endpoint_key, pattern):
                return permission
        
        return None
    
    def _matches_pattern(self, endpoint: str, pattern: str) -> bool:
        """Check if endpoint matches pattern (simple implementation)."""
        # This could be enhanced with regex or more sophisticated matching
        endpoint_parts = endpoint.split()
        pattern_parts = pattern.split()
        
        if len(endpoint_parts) != len(pattern_parts):
            return False
        
        method_match = endpoint_parts[0] == pattern_parts[0]
        path_match = endpoint_parts[1].startswith(pattern_parts[1].rstrip('*'))
        
        return method_match and path_match