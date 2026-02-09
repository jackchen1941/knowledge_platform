"""
Authentication CLI Commands

Command-line interface for managing authentication system.
"""

import asyncio
import click
from loguru import logger

from app.core.init_auth import initialize_auth_system, reset_auth_system, create_admin_user, create_default_user
from app.core.database import get_db
from app.services.auth import AuthService
from app.services.permission import PermissionService
from app.schemas.auth import UserRegister


@click.group()
def auth():
    """Authentication management commands."""
    pass


@auth.command()
def init():
    """Initialize authentication system with default roles, permissions, and users."""
    click.echo("Initializing authentication system...")
    
    try:
        asyncio.run(initialize_auth_system())
        click.echo("✅ Authentication system initialized successfully!")
        click.echo("Default credentials:")
        click.echo("  Admin: admin@example.com / admin123")
        click.echo("  User:  user@example.com / user123")
    except Exception as e:
        click.echo(f"❌ Failed to initialize authentication system: {e}")
        raise click.Abort()


@auth.command()
@click.confirmation_option(prompt="Are you sure you want to reset the authentication system?")
def reset():
    """Reset authentication system (WARNING: This will delete all users and roles)."""
    click.echo("Resetting authentication system...")
    
    try:
        asyncio.run(reset_auth_system())
        click.echo("✅ Authentication system reset successfully!")
    except Exception as e:
        click.echo(f"❌ Failed to reset authentication system: {e}")
        raise click.Abort()


@auth.command()
@click.option("--username", prompt=True, help="Username for the admin user")
@click.option("--email", prompt=True, help="Email for the admin user")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the admin user")
def create_admin(username: str, email: str, password: str):
    """Create a new admin user."""
    
    async def _create_admin():
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            admin_user = await create_admin_user(db, username, email, password)
            return admin_user
        finally:
            await db.close()
    
    try:
        admin_user = asyncio.run(_create_admin())
        click.echo(f"✅ Admin user created successfully!")
        click.echo(f"   ID: {admin_user.id}")
        click.echo(f"   Username: {admin_user.username}")
        click.echo(f"   Email: {admin_user.email}")
    except Exception as e:
        click.echo(f"❌ Failed to create admin user: {e}")
        raise click.Abort()


@auth.command()
@click.option("--username", prompt=True, help="Username for the user")
@click.option("--email", prompt=True, help="Email for the user")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the user")
@click.option("--role", default="user", help="Role to assign to the user")
def create_user(username: str, email: str, password: str, role: str):
    """Create a new user."""
    
    async def _create_user():
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            auth_service = AuthService(db)
            permission_service = PermissionService(db)
            
            # Create user
            user_data = UserRegister(
                username=username,
                email=email,
                password=password
            )
            
            user = await auth_service.register_user(user_data)
            
            # Make user verified and active
            user.is_verified = True
            user.is_active = True
            await db.commit()
            await db.refresh(user)
            
            # Assign role
            user_role = await permission_service.get_role_by_name(role)
            if user_role:
                await permission_service.assign_role_to_user(
                    user_id=user.id,
                    role_id=user_role.id,
                    assigned_by="system"
                )
            
            return user
            
        finally:
            await db.close()
    
    try:
        user = asyncio.run(_create_user())
        click.echo(f"✅ User created successfully!")
        click.echo(f"   ID: {user.id}")
        click.echo(f"   Username: {user.username}")
        click.echo(f"   Email: {user.email}")
        click.echo(f"   Role: {role}")
    except Exception as e:
        click.echo(f"❌ Failed to create user: {e}")
        raise click.Abort()


@auth.command()
def list_users():
    """List all users in the system."""
    
    async def _list_users():
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            from sqlalchemy import select
            from app.models.user import User
            
            result = await db.execute(select(User).order_by(User.created_at))
            users = result.scalars().all()
            
            return users
            
        finally:
            await db.close()
    
    try:
        users = asyncio.run(_list_users())
        
        if not users:
            click.echo("No users found.")
            return
        
        click.echo(f"Found {len(users)} users:")
        click.echo()
        
        for user in users:
            status = "✅" if user.is_active else "❌"
            verified = "✓" if user.is_verified else "✗"
            superuser = "👑" if user.is_superuser else ""
            
            click.echo(f"{status} {user.username} ({user.email})")
            click.echo(f"   ID: {user.id}")
            click.echo(f"   Verified: {verified} | Superuser: {superuser}")
            click.echo(f"   Created: {user.created_at}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Failed to list users: {e}")
        raise click.Abort()


@auth.command()
def list_roles():
    """List all roles in the system."""
    
    async def _list_roles():
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            permission_service = PermissionService(db)
            roles = await permission_service.list_roles()
            return roles
            
        finally:
            await db.close()
    
    try:
        roles = asyncio.run(_list_roles())
        
        if not roles:
            click.echo("No roles found.")
            return
        
        click.echo(f"Found {len(roles)} roles:")
        click.echo()
        
        for role in roles:
            status = "✅" if role.is_active else "❌"
            system = "🔒" if role.is_system else ""
            
            click.echo(f"{status} {role.name} - {role.display_name} {system}")
            click.echo(f"   ID: {role.id}")
            click.echo(f"   Description: {role.description or 'No description'}")
            click.echo(f"   Priority: {role.priority}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Failed to list roles: {e}")
        raise click.Abort()


@auth.command()
def list_permissions():
    """List all permissions in the system."""
    
    async def _list_permissions():
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            permission_service = PermissionService(db)
            permissions = await permission_service.list_permissions()
            return permissions
            
        finally:
            await db.close()
    
    try:
        permissions = asyncio.run(_list_permissions())
        
        if not permissions:
            click.echo("No permissions found.")
            return
        
        click.echo(f"Found {len(permissions)} permissions:")
        click.echo()
        
        # Group by resource
        by_resource = {}
        for perm in permissions:
            if perm.resource not in by_resource:
                by_resource[perm.resource] = []
            by_resource[perm.resource].append(perm)
        
        for resource, perms in by_resource.items():
            click.echo(f"📁 {resource.upper()}")
            for perm in perms:
                status = "✅" if perm.is_active else "❌"
                system = "🔒" if perm.is_system else ""
                
                click.echo(f"   {status} {perm.action} - {perm.display_name} {system}")
                click.echo(f"      Name: {perm.name}")
                if perm.description:
                    click.echo(f"      Description: {perm.description}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Failed to list permissions: {e}")
        raise click.Abort()


if __name__ == "__main__":
    auth()