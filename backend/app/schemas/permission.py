"""
Permission Schemas

Pydantic models for permission-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base permission schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


class PermissionCreate(PermissionBase):
    """Permission creation schema."""
    is_system: bool = False


class PermissionUpdate(BaseModel):
    """Permission update schema."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """Permission response schema."""
    id: str
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RolePermissionBase(BaseModel):
    """Base role-permission assignment schema."""
    role_id: str
    permission_id: str
    granted: bool = True


class RolePermissionCreate(RolePermissionBase):
    """Role-permission assignment creation schema."""
    pass


class RolePermissionResponse(RolePermissionBase):
    """Role-permission assignment response schema."""
    created_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class UserPermissionBase(BaseModel):
    """Base user-permission assignment schema."""
    user_id: str
    permission_id: str
    granted: bool = True
    expires_at: Optional[datetime] = None


class UserPermissionCreate(UserPermissionBase):
    """User-permission assignment creation schema."""
    pass


class UserPermissionResponse(UserPermissionBase):
    """User-permission assignment response schema."""
    granted_at: datetime
    granted_by: str
    is_active: bool
    
    class Config:
        from_attributes = True


class PermissionCheckRequest(BaseModel):
    """Permission check request schema."""
    user_id: str
    permission_name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionCheckResponse(BaseModel):
    """Permission check response schema."""
    user_id: str
    permission_name: str
    granted: bool
    source: str  # "role" or "direct" or "denied"


class UserPermissionsResponse(BaseModel):
    """User permissions list response schema."""
    user_id: str
    permissions: List[str]
    roles: List[str]