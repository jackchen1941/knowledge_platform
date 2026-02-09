"""
Permission Service

Business logic for role-based access control and permission management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Set, Tuple

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.core.exceptions import AuthorizationError, ValidationError, NotFoundError
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission, RolePermission, UserRole, UserPermission
from app.core.security import AuditLogger


class PermissionService:
    """Service class for permission and role management operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Role Management
    async def create_role(self, name: str, display_name: str, description: str = None, 
                         created_by: str = None, is_system: bool = False) -> Role:
        """Create a new role."""
        
        # Check if role already exists
        existing_role = await self.get_role_by_name(name)
        if existing_role:
            raise ValidationError(f"Role '{name}' already exists")
        
        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            is_system=is_system
        )
        
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        logger.info(f"Role created: {role.name} by user {created_by}")
        return role
    
    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).where(Role.name == name, Role.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def list_roles(self, include_system: bool = True) -> List[Role]:
        """List all active roles."""
        query = select(Role).where(Role.is_active == True)
        
        if not include_system:
            query = query.where(Role.is_system == False)
        
        result = await self.db.execute(query.order_by(Role.priority.desc(), Role.name))
        return result.scalars().all()
    
    async def update_role(self, role_id: str, **updates) -> Role:
        """Update role information."""
        role = await self.get_role_by_id(role_id)
        if not role:
            raise NotFoundError("Role not found")
        
        if role.is_system and 'name' in updates:
            raise ValidationError("Cannot modify system role name")
        
        for field, value in updates.items():
            if hasattr(role, field):
                setattr(role, field, value)
        
        role.updated_at = datetime.utcnow()
        await self.db.commit()
        
        return role
    
    async def delete_role(self, role_id: str, deleted_by: str) -> bool:
        """Delete a role (soft delete)."""
        role = await self.get_role_by_id(role_id)
        if not role:
            return False
        
        if role.is_system:
            raise ValidationError("Cannot delete system role")
        
        # Check if role is assigned to any users
        result = await self.db.execute(
            select(UserRole).where(UserRole.role_id == role_id, UserRole.is_active == True)
        )
        if result.scalar_one_or_none():
            raise ValidationError("Cannot delete role that is assigned to users")
        
        role.is_active = False
        role.updated_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info(f"Role deleted: {role.name} by user {deleted_by}")
        return True
    
    # Permission Management
    async def create_permission(self, name: str, display_name: str, resource: str, 
                              action: str, description: str = None, is_system: bool = False) -> Permission:
        """Create a new permission."""
        
        # Check if permission already exists
        existing_permission = await self.get_permission_by_name(name)
        if existing_permission:
            raise ValidationError(f"Permission '{name}' already exists")
        
        permission = Permission(
            name=name,
            display_name=display_name,
            description=description,
            resource=resource,
            action=action,
            is_system=is_system
        )
        
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        
        logger.info(f"Permission created: {permission.name}")
        return permission
    
    async def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id, Permission.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        result = await self.db.execute(
            select(Permission).where(Permission.name == name, Permission.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def list_permissions(self, resource: str = None, action: str = None) -> List[Permission]:
        """List permissions with optional filtering."""
        query = select(Permission).where(Permission.is_active == True)
        
        if resource:
            query = query.where(Permission.resource == resource)
        if action:
            query = query.where(Permission.action == action)
        
        result = await self.db.execute(query.order_by(Permission.resource, Permission.action))
        return result.scalars().all()
    
    # Role-Permission Assignment
    async def assign_permission_to_role(self, role_id: str, permission_id: str, 
                                      granted: bool = True, assigned_by: str = None) -> RolePermission:
        """Assign a permission to a role."""
        
        # Verify role and permission exist
        role = await self.get_role_by_id(role_id)
        permission = await self.get_permission_by_id(permission_id)
        
        if not role:
            raise NotFoundError("Role not found")
        if not permission:
            raise NotFoundError("Permission not found")
        
        # Check if assignment already exists
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.granted = granted
            existing.created_by = assigned_by or "system"
            existing.created_at = datetime.utcnow()
            await self.db.commit()
            return existing
        
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
            granted=granted,
            created_by=assigned_by or "system"
        )
        
        self.db.add(role_permission)
        await self.db.commit()
        
        logger.info(f"Permission {permission.name} {'granted to' if granted else 'denied from'} role {role.name}")
        return role_permission
    
    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Remove a permission from a role."""
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        )
        role_permission = result.scalar_one_or_none()
        
        if role_permission:
            await self.db.delete(role_permission)
            await self.db.commit()
            return True
        
        return False
    
    # User-Role Assignment
    async def assign_role_to_user(self, user_id: str, role_id: str, 
                                assigned_by: str, expires_at: datetime = None) -> UserRole:
        """Assign a role to a user."""
        
        # Verify user and role exist
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        role = await self.get_role_by_id(role_id)
        
        if not user_result.scalar_one_or_none():
            raise NotFoundError("User not found")
        if not role:
            raise NotFoundError("Role not found")
        
        # Check if assignment already exists
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.is_active = True
            existing.assigned_by = assigned_by
            existing.assigned_at = datetime.utcnow()
            existing.expires_at = expires_at
            await self.db.commit()
            return existing
        
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        
        self.db.add(user_role)
        await self.db.commit()
        
        logger.info(f"Role {role.name} assigned to user {user_id} by {assigned_by}")
        return user_role
    
    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user."""
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_active == True
            )
        )
        user_role = result.scalar_one_or_none()
        
        if user_role:
            user_role.is_active = False
            await self.db.commit()
            return True
        
        return False
    
    # User-Permission Direct Assignment
    async def assign_permission_to_user(self, user_id: str, permission_id: str, 
                                      granted: bool = True, granted_by: str = None,
                                      expires_at: datetime = None) -> UserPermission:
        """Directly assign a permission to a user."""
        
        # Verify user and permission exist
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        permission = await self.get_permission_by_id(permission_id)
        
        if not user_result.scalar_one_or_none():
            raise NotFoundError("User not found")
        if not permission:
            raise NotFoundError("Permission not found")
        
        # Check if assignment already exists
        result = await self.db.execute(
            select(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.granted = granted
            existing.granted_by = granted_by or "system"
            existing.granted_at = datetime.utcnow()
            existing.expires_at = expires_at
            existing.is_active = True
            await self.db.commit()
            return existing
        
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            granted=granted,
            granted_by=granted_by or "system",
            expires_at=expires_at
        )
        
        self.db.add(user_permission)
        await self.db.commit()
        
        logger.info(f"Permission {permission.name} {'granted to' if granted else 'denied from'} user {user_id}")
        return user_permission
    
    # Permission Checking
    async def check_user_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if a user has a specific permission."""
        
        # Get permission
        permission = await self.get_permission_by_name(permission_name)
        if not permission:
            return False
        
        # Check direct user permissions first (highest priority)
        result = await self.db.execute(
            select(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission.id,
                UserPermission.is_active == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        )
        user_permission = result.scalar_one_or_none()
        
        if user_permission:
            AuditLogger.log_permission_check(user_id, permission.resource, permission.action, user_permission.granted)
            return user_permission.granted
        
        # Check role-based permissions
        result = await self.db.execute(
            select(RolePermission).join(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                ),
                RolePermission.permission_id == permission.id
            )
        )
        role_permissions = result.scalars().all()
        
        # If any role explicitly denies, deny access
        for rp in role_permissions:
            if not rp.granted:
                AuditLogger.log_permission_check(user_id, permission.resource, permission.action, False)
                return False
        
        # If any role grants, allow access
        for rp in role_permissions:
            if rp.granted:
                AuditLogger.log_permission_check(user_id, permission.resource, permission.action, True)
                return True
        
        # No permissions found
        AuditLogger.log_permission_check(user_id, permission.resource, permission.action, False)
        return False
    
    async def check_user_permission_by_resource_action(self, user_id: str, resource: str, action: str) -> bool:
        """Check if a user has permission for a specific resource and action."""
        
        # Find permission by resource and action
        result = await self.db.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action == action,
                Permission.is_active == True
            )
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            return False
        
        return await self.check_user_permission(user_id, permission.name)
    
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user."""
        
        permissions = set()
        
        # Get direct user permissions
        result = await self.db.execute(
            select(Permission.name).join(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.is_active == True,
                UserPermission.granted == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        )
        permissions.update(result.scalars().all())
        
        # Get role-based permissions
        result = await self.db.execute(
            select(Permission.name).join(RolePermission).join(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                ),
                RolePermission.granted == True
            )
        )
        permissions.update(result.scalars().all())
        
        # Remove explicitly denied permissions
        result = await self.db.execute(
            select(Permission.name).join(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.is_active == True,
                UserPermission.granted == False,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.utcnow()
                )
            )
        )
        denied_permissions = set(result.scalars().all())
        permissions -= denied_permissions
        
        return permissions
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all active roles for a user."""
        
        result = await self.db.execute(
            select(Role).join(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                ),
                Role.is_active == True
            ).options(selectinload(Role.permissions))
        )
        
        return result.scalars().all()


async def initialize_default_roles_and_permissions(db: AsyncSession):
    """Initialize default system roles and permissions."""
    
    permission_service = PermissionService(db)
    
    # Default permissions
    default_permissions = [
        # Knowledge management
        ("knowledge.create", "Create Knowledge", "knowledge_item", "create"),
        ("knowledge.read", "Read Knowledge", "knowledge_item", "read"),
        ("knowledge.update", "Update Knowledge", "knowledge_item", "update"),
        ("knowledge.delete", "Delete Knowledge", "knowledge_item", "delete"),
        ("knowledge.publish", "Publish Knowledge", "knowledge_item", "publish"),
        
        # Category management
        ("category.create", "Create Category", "category", "create"),
        ("category.read", "Read Category", "category", "read"),
        ("category.update", "Update Category", "category", "update"),
        ("category.delete", "Delete Category", "category", "delete"),
        
        # Tag management
        ("tag.create", "Create Tag", "tag", "create"),
        ("tag.read", "Read Tag", "tag", "read"),
        ("tag.update", "Update Tag", "tag", "update"),
        ("tag.delete", "Delete Tag", "tag", "delete"),
        
        # User management
        ("user.read", "Read User", "user", "read"),
        ("user.update", "Update User", "user", "update"),
        ("user.delete", "Delete User", "user", "delete"),
        ("user.manage_roles", "Manage User Roles", "user", "manage_roles"),
        
        # System administration
        ("system.admin", "System Administration", "system", "admin"),
        ("system.config", "System Configuration", "system", "config"),
        ("system.logs", "View System Logs", "system", "logs"),
        
        # Import/Export
        ("import.create", "Create Import Config", "import", "create"),
        ("import.execute", "Execute Import", "import", "execute"),
        ("export.execute", "Execute Export", "export", "execute"),
    ]
    
    # Create permissions
    for name, display_name, resource, action in default_permissions:
        try:
            await permission_service.create_permission(
                name=name,
                display_name=display_name,
                resource=resource,
                action=action,
                is_system=True
            )
        except ValidationError:
            # Permission already exists
            pass
    
    # Default roles
    default_roles = [
        ("admin", "Administrator", "Full system access"),
        ("editor", "Editor", "Can create and edit content"),
        ("viewer", "Viewer", "Can only view content"),
        ("user", "Regular User", "Basic user permissions"),
    ]
    
    # Create roles
    for name, display_name, description in default_roles:
        try:
            await permission_service.create_role(
                name=name,
                display_name=display_name,
                description=description,
                is_system=True
            )
        except ValidationError:
            # Role already exists
            pass
    
    # Assign permissions to roles
    role_permissions = {
        "admin": [p[0] for p in default_permissions],  # All permissions
        "editor": [
            "knowledge.create", "knowledge.read", "knowledge.update", "knowledge.delete", "knowledge.publish",
            "category.create", "category.read", "category.update", "category.delete",
            "tag.create", "tag.read", "tag.update", "tag.delete",
            "import.create", "import.execute", "export.execute"
        ],
        "viewer": [
            "knowledge.read", "category.read", "tag.read"
        ],
        "user": [
            "knowledge.create", "knowledge.read", "knowledge.update", "knowledge.delete",
            "category.create", "category.read", "category.update", "category.delete",
            "tag.create", "tag.read", "tag.update", "tag.delete"
        ]
    }
    
    for role_name, permission_names in role_permissions.items():
        role = await permission_service.get_role_by_name(role_name)
        if role:
            for permission_name in permission_names:
                permission = await permission_service.get_permission_by_name(permission_name)
                if permission:
                    try:
                        await permission_service.assign_permission_to_role(
                            role.id, permission.id, granted=True, assigned_by="system"
                        )
                    except Exception:
                        # Assignment already exists
                        pass
    
    logger.info("Default roles and permissions initialized")