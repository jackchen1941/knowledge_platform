"""
Role Management Endpoints

Handles role-based access control operations.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security, get_current_user_id, AuditLogger
from app.services.permission import PermissionService
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions,
    UserRoleCreate, UserRoleResponse, UserRolesResponse
)
from app.schemas.permission import RolePermissionCreate, RolePermissionResponse

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new role."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to create roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create roles"
        )
    
    try:
        role = await permission_service.create_role(
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            created_by=current_user_id,
            is_system=role_data.is_system
        )
        
        AuditLogger.log_security_event(
            "ROLE_CREATED",
            {
                "role_id": role.id,
                "role_name": role.name,
                "created_by": current_user_id
            }
        )
        
        return role
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    include_system: bool = True,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all roles."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to view roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view roles"
        )
    
    roles = await permission_service.list_roles(include_system=include_system)
    return roles


@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific role by ID with its permissions."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to view roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view roles"
        )
    
    role = await permission_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Get role permissions
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.role import Role
    
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permissions))
    )
    role_with_permissions = result.scalar_one_or_none()
    
    if not role_with_permissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Convert to response format
    permissions = []
    for rp in role_with_permissions.permissions:
        if rp.granted:  # Only include granted permissions
            permissions.append(rp.permission)
    
    return RoleWithPermissions(
        **role.__dict__,
        permissions=permissions
    )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a role."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to update roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update roles"
        )
    
    try:
        update_data = role_data.dict(exclude_unset=True)
        role = await permission_service.update_role(role_id, **update_data)
        
        AuditLogger.log_security_event(
            "ROLE_UPDATED",
            {
                "role_id": role.id,
                "role_name": role.name,
                "updated_by": current_user_id,
                "changes": update_data
            }
        )
        
        return role
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a role."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to delete roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete roles"
        )
    
    try:
        success = await permission_service.delete_role(role_id, current_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        AuditLogger.log_security_event(
            "ROLE_DELETED",
            {
                "role_id": role_id,
                "deleted_by": current_user_id
            }
        )
        
        return {"message": "Role deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{role_id}/permissions", response_model=RolePermissionResponse)
async def assign_permission_to_role(
    role_id: str,
    permission_data: RolePermissionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Assign a permission to a role."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage role permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign role permissions"
        )
    
    try:
        role_permission = await permission_service.assign_permission_to_role(
            role_id=role_id,
            permission_id=permission_data.permission_id,
            granted=permission_data.granted,
            assigned_by=current_user_id
        )
        
        AuditLogger.log_security_event(
            "ROLE_PERMISSION_ASSIGNED",
            {
                "role_id": role_id,
                "permission_id": permission_data.permission_id,
                "granted": permission_data.granted,
                "assigned_by": current_user_id
            }
        )
        
        return role_permission
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Remove a permission from a role."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage role permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove role permissions"
        )
    
    success = await permission_service.remove_permission_from_role(role_id, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission not found"
        )
    
    AuditLogger.log_security_event(
        "ROLE_PERMISSION_REMOVED",
        {
            "role_id": role_id,
            "permission_id": permission_id,
            "removed_by": current_user_id
        }
    )
    
    return {"message": "Permission removed from role successfully"}


@router.post("/users/{user_id}/roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_id: str,
    role_data: UserRoleCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Assign a role to a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage user roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "user.manage_roles"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign user roles"
        )
    
    try:
        user_role = await permission_service.assign_role_to_user(
            user_id=user_id,
            role_id=role_data.role_id,
            assigned_by=current_user_id,
            expires_at=role_data.expires_at
        )
        
        AuditLogger.log_security_event(
            "USER_ROLE_ASSIGNED",
            {
                "user_id": user_id,
                "role_id": role_data.role_id,
                "assigned_by": current_user_id
            }
        )
        
        return user_role
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Remove a role from a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage user roles
    has_permission = await permission_service.check_user_permission(
        current_user_id, "user.manage_roles"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove user roles"
        )
    
    success = await permission_service.remove_role_from_user(user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User role not found"
        )
    
    AuditLogger.log_security_event(
        "USER_ROLE_REMOVED",
        {
            "user_id": user_id,
            "role_id": role_id,
            "removed_by": current_user_id
        }
    )
    
    return {"message": "Role removed from user successfully"}


@router.get("/users/{user_id}/roles", response_model=UserRolesResponse)
async def get_user_roles(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all roles for a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Users can view their own roles, or admins can view any user's roles
    if user_id != current_user_id:
        has_admin_permission = await permission_service.check_user_permission(
            current_user_id, "user.read"
        )
        if not has_admin_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view other users' roles"
            )
    
    roles = await permission_service.get_user_roles(user_id)
    
    return UserRolesResponse(
        user_id=user_id,
        roles=roles
    )