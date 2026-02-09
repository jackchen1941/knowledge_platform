"""
Role Schemas

Pydantic models for role-related requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .permission import PermissionResponse


class RoleBase(BaseModel):
    """Base role schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: int = Field(default=0, ge=0)


class RoleCreate(RoleBase):
    """Role creation schema."""
    is_system: bool = False


class RoleUpdate(BaseModel):
    """Role update schema."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Role response schema."""
    id: str
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Role response with permissions included."""
    permissions: List[PermissionResponse] = []


class UserRoleBase(BaseModel):
    """Base user-role assignment schema."""
    user_id: str
    role_id: str
    expires_at: Optional[datetime] = None


class UserRoleCreate(UserRoleBase):
    """User-role assignment creation schema."""
    pass


class UserRoleResponse(UserRoleBase):
    """User-role assignment response schema."""
    assigned_at: datetime
    assigned_by: str
    is_active: bool
    
    class Config:
        from_attributes = True


class UserRolesResponse(BaseModel):
    """User roles list response schema."""
    user_id: str
    roles: List[RoleResponse]