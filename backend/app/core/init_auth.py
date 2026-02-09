"""
Authentication System Initialization

Initialize default roles, permissions, and admin user.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.database import get_db
from app.core.security import PasswordManager
from app.services.permission import PermissionService, initialize_default_roles_and_permissions
from app.services.auth import AuthService
from app.models.user import User
from app.schemas.auth import UserRegister


async def create_admin_user(db: AsyncSession, username: str = "admin", 
                          email: str = "admin@example.com", 
                          password: str = "admin123") -> User:
    """Create the initial admin user."""
    
    auth_service = AuthService(db)
    permission_service = PermissionService(db)
    
    # Check if admin user already exists
    existing_user = await auth_service.get_user_by_email(email)
    if existing_user:
        logger.info(f"Admin user already exists: {email}")
        return existing_user
    
    # Create admin user
    try:
        admin_user_data = UserRegister(
            username=username,
            email=email,
            password=password,
            full_name="System Administrator"
        )
        
        admin_user = await auth_service.register_user(admin_user_data)
        
        # Make user verified and active
        admin_user.is_verified = True
        admin_user.is_active = True
        admin_user.is_superuser = True
        
        await db.commit()
        await db.refresh(admin_user)
        
        # Assign admin role
        admin_role = await permission_service.get_role_by_name("admin")
        if admin_role:
            await permission_service.assign_role_to_user(
                user_id=admin_user.id,
                role_id=admin_role.id,
                assigned_by="system"
            )
        
        logger.info(f"Admin user created successfully: {email}")
        return admin_user
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise


async def create_default_user(db: AsyncSession, username: str = "user", 
                            email: str = "user@example.com", 
                            password: str = "user123") -> User:
    """Create a default regular user for testing."""
    
    auth_service = AuthService(db)
    permission_service = PermissionService(db)
    
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(email)
    if existing_user:
        logger.info(f"Default user already exists: {email}")
        return existing_user
    
    try:
        user_data = UserRegister(
            username=username,
            email=email,
            password=password,
            full_name="Default User"
        )
        
        user = await auth_service.register_user(user_data)
        
        # Make user verified and active
        user.is_verified = True
        user.is_active = True
        
        await db.commit()
        await db.refresh(user)
        
        # Assign user role
        user_role = await permission_service.get_role_by_name("user")
        if user_role:
            await permission_service.assign_role_to_user(
                user_id=user.id,
                role_id=user_role.id,
                assigned_by="system"
            )
        
        logger.info(f"Default user created successfully: {email}")
        return user
        
    except Exception as e:
        logger.error(f"Failed to create default user: {e}")
        raise


async def initialize_auth_system():
    """Initialize the complete authentication system."""
    
    logger.info("Initializing authentication system...")
    
    # Get database session
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # 1. Initialize default roles and permissions
        logger.info("Creating default roles and permissions...")
        await initialize_default_roles_and_permissions(db)
        
        # 2. Create admin user
        logger.info("Creating admin user...")
        admin_user = await create_admin_user(db)
        
        # 3. Create default user
        logger.info("Creating default user...")
        default_user = await create_default_user(db)
        
        logger.info("Authentication system initialized successfully!")
        logger.info(f"Admin user: admin@example.com / admin123")
        logger.info(f"Default user: user@example.com / user123")
        
        return {
            "admin_user": admin_user,
            "default_user": default_user
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize authentication system: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


async def reset_auth_system():
    """Reset the authentication system (for development/testing)."""
    
    logger.warning("Resetting authentication system...")
    
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # Delete all users, roles, and permissions (except system ones)
        from sqlalchemy import delete
        from app.models.user import User
        from app.models.role import Role
        from app.models.permission import Permission, UserRole, UserPermission, RolePermission
        
        # Delete user assignments
        await db.execute(delete(UserRole))
        await db.execute(delete(UserPermission))
        await db.execute(delete(RolePermission))
        
        # Delete non-system users
        await db.execute(delete(User).where(User.is_superuser == False))
        
        # Delete non-system roles and permissions
        await db.execute(delete(Role).where(Role.is_system == False))
        await db.execute(delete(Permission).where(Permission.is_system == False))
        
        await db.commit()
        
        # Reinitialize
        await initialize_auth_system()
        
        logger.info("Authentication system reset completed!")
        
    except Exception as e:
        logger.error(f"Failed to reset authentication system: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


def main():
    """Main function to run initialization."""
    asyncio.run(initialize_auth_system())


if __name__ == "__main__":
    main()