"""
Custom Exception Classes

Defines custom exceptions for the knowledge management platform
with proper error codes and messages.
"""

from typing import Any, Dict, Optional


class KMPException(Exception):
    """Base exception class for Knowledge Management Platform."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.message)


class ValidationError(KMPException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=400, detail=detail)


class AuthenticationError(KMPException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        super().__init__(
            message,
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(KMPException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions", detail: Optional[str] = None):
        super().__init__(message, status_code=403, detail=detail)


class PermissionError(KMPException):
    """Raised when user doesn't have permission for an operation."""
    
    def __init__(self, message: str = "Permission denied", detail: Optional[str] = None):
        super().__init__(message, status_code=403, detail=detail)


class NotFoundError(KMPException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(message, status_code=404, detail=detail)


class ConflictError(KMPException):
    """Raised when a resource conflict occurs."""
    
    def __init__(self, message: str = "Resource conflict", detail: Optional[str] = None):
        super().__init__(message, status_code=409, detail=detail)


class RateLimitError(KMPException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", detail: Optional[str] = None):
        super().__init__(message, status_code=429, detail=detail)


class ExternalServiceError(KMPException):
    """Raised when external service integration fails."""
    
    def __init__(self, message: str = "External service error", detail: Optional[str] = None):
        super().__init__(message, status_code=502, detail=detail)


class DatabaseError(KMPException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class FileProcessingError(KMPException):
    """Raised when file processing fails."""
    
    def __init__(self, message: str = "File processing failed", detail: Optional[str] = None):
        super().__init__(message, status_code=422, detail=detail)


class SecurityError(KMPException):
    """Raised when security violations are detected."""
    
    def __init__(self, message: str = "Security violation detected", detail: Optional[str] = None):
        super().__init__(message, status_code=403, detail=detail)