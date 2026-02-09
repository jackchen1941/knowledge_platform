"""
Permission Management Endpoints

Handles permission and role-based access control operations.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security, get_current_user_id, AuditLogger
from app.services.permission import PermissionService
from app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RolePermissionCreate, RolePermissionResponse,
    UserPermissionCreate, UserPermissionResponse,
    PermissionCheckRequest, PermissionCheckResponse,
    UserPermissionsResponse
)

router = APIRouter()


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new permission."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to create permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create permissions"
        )
    
    try:
        permission = await permission_service.create_permission(
            name=permission_data.name,
            display_name=permission_data.display_name,
            resource=permission_data.resource,
            action=permission_data.action,
            description=permission_data.description,
            is_system=permission_data.is_system
        )
        
        AuditLogger.log_security_event(
            "PERMISSION_CREATED",
            {
                "permission_id": permission.id,
                "permission_name": permission.name,
                "created_by": current_user_id
            }
        )
        
        return permission
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[PermissionResponse])
async def list_permissions(
    resource: str = None,
    action: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all permissions with optional filtering."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to view permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view permissions"
        )
    
    permissions = await permission_service.list_permissions(resource=resource, action=action)
    return permissions


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific permission by ID."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to view permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view permissions"
        )
    
    permission = await permission_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a permission."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to update permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update permissions"
        )
    
    try:
        permission = await permission_service.get_permission_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Update permission fields
        update_data = permission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        await db.commit()
        await db.refresh(permission)
        
        AuditLogger.log_security_event(
            "PERMISSION_UPDATED",
            {
                "permission_id": permission.id,
                "permission_name": permission.name,
                "updated_by": current_user_id,
                "changes": update_data
            }
        )
        
        return permission
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a permission."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to delete permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "system.admin"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete permissions"
        )
    
    permission = await permission_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    if permission.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system permission"
        )
    
    permission.is_active = False
    await db.commit()
    
    AuditLogger.log_security_event(
        "PERMISSION_DELETED",
        {
            "permission_id": permission.id,
            "permission_name": permission.name,
            "deleted_by": current_user_id
        }
    )
    
    return {"message": "Permission deleted successfully"}


@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_request: PermissionCheckRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Check if a user has a specific permission."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Users can check their own permissions, or admins can check any user's permissions
    if check_request.user_id != current_user_id:
        has_admin_permission = await permission_service.check_user_permission(
            current_user_id, "user.read"
        )
        if not has_admin_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to check other users' permissions"
            )
    
    # Check permission by name or resource/action
    if check_request.permission_name:
        granted = await permission_service.check_user_permission(
            check_request.user_id, check_request.permission_name
        )
        permission_name = check_request.permission_name
    elif check_request.resource and check_request.action:
        granted = await permission_service.check_user_permission_by_resource_action(
            check_request.user_id, check_request.resource, check_request.action
        )
        permission_name = f"{check_request.resource}.{check_request.action}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either permission_name or both resource and action"
        )
    
    return PermissionCheckResponse(
        user_id=check_request.user_id,
        permission_name=permission_name,
        granted=granted,
        source="role"  # Simplified - could be enhanced to show actual source
    )


@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all permissions for a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Users can view their own permissions, or admins can view any user's permissions
    if user_id != current_user_id:
        has_admin_permission = await permission_service.check_user_permission(
            current_user_id, "user.read"
        )
        if not has_admin_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view other users' permissions"
            )
    
    permissions = await permission_service.get_user_permissions(user_id)
    roles = await permission_service.get_user_roles(user_id)
    
    return UserPermissionsResponse(
        user_id=user_id,
        permissions=list(permissions),
        roles=[role.name for role in roles]
    )


@router.post("/users/{user_id}/permissions", response_model=UserPermissionResponse)
async def assign_permission_to_user(
    user_id: str,
    permission_data: UserPermissionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Assign a permission directly to a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage user permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "user.manage_roles"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign user permissions"
        )
    
    try:
        user_permission = await permission_service.assign_permission_to_user(
            user_id=user_id,
            permission_id=permission_data.permission_id,
            granted=permission_data.granted,
            granted_by=current_user_id,
            expires_at=permission_data.expires_at
        )
        
        AuditLogger.log_security_event(
            "USER_PERMISSION_ASSIGNED",
            {
                "user_id": user_id,
                "permission_id": permission_data.permission_id,
                "granted": permission_data.granted,
                "assigned_by": current_user_id
            }
        )
        
        return user_permission
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/users/{user_id}/permissions/{permission_id}")
async def remove_permission_from_user(
    user_id: str,
    permission_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Remove a direct permission from a user."""
    current_user_id = get_current_user_id(credentials)
    permission_service = PermissionService(db)
    
    # Check if user has permission to manage user permissions
    has_permission = await permission_service.check_user_permission(
        current_user_id, "user.manage_roles"
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove user permissions"
        )
    
    # Remove the user permission by setting it to inactive
    from sqlalchemy import select, update
    from app.models.permission import UserPermission
    
    result = await db.execute(
        update(UserPermission)
        .where(
            UserPermission.user_id == user_id,
            UserPermission.permission_id == permission_id
        )
        .values(is_active=False)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User permission not found"
        )
    
    await db.commit()
    
    AuditLogger.log_security_event(
        "USER_PERMISSION_REMOVED",
        {
            "user_id": user_id,
            "permission_id": permission_id,
            "removed_by": current_user_id
        }
    )
    
    return {"message": "Permission removed from user successfully"}