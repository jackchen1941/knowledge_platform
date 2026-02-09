#!/usr/bin/env python3
"""
Run authentication system test and start server if successful.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./knowledge_platform.db'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

async def setup_auth_system():
    """Set up the authentication system."""
    
    print("🚀 Setting up Knowledge Management Platform Authentication...")
    
    try:
        from app.core.database import init_database, create_tables, get_db
        from app.services.auth import AuthService
        from app.services.permission import PermissionService, initialize_default_roles_and_permissions
        from app.schemas.auth import UserRegister
        
        # Initialize database
        print("📊 Initializing database...")
        await init_database()
        
        # Create tables
        print("🏗️  Creating tables...")
        await create_tables()
        
        # Initialize roles and permissions
        print("🔐 Setting up roles and permissions...")
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            await initialize_default_roles_and_permissions(db)
            
            # Create admin user
            print("👑 Creating admin user...")
            auth_service = AuthService(db)
            permission_service = PermissionService(db)
            
            # Check if admin already exists
            existing_admin = await auth_service.get_user_by_email("admin@example.com")
            if not existing_admin:
                admin_data = UserRegister(
                    username="admin",
                    email="admin@example.com",
                    password="admin123",
                    full_name="System Administrator"
                )
                
                admin_user = await auth_service.register_user(admin_data)
                admin_user.is_verified = True
                admin_user.is_superuser = True
                await db.commit()
                
                # Assign admin role
                admin_role = await permission_service.get_role_by_name("admin")
                if admin_role:
                    await permission_service.assign_role_to_user(
                        user_id=admin_user.id,
                        role_id=admin_role.id,
                        assigned_by="system"
                    )
                
                print(f"✅ Admin user created: {admin_user.email}")
            else:
                print("✅ Admin user already exists")
            
            # Create regular user
            print("👤 Creating regular user...")
            existing_user = await auth_service.get_user_by_email("user@example.com")
            if not existing_user:
                user_data = UserRegister(
                    username="user",
                    email="user@example.com",
                    password="user123",
                    full_name="Regular User"
                )
                
                regular_user = await auth_service.register_user(user_data)
                regular_user.is_verified = True
                await db.commit()
                
                # Assign user role
                user_role = await permission_service.get_role_by_name("user")
                if user_role:
                    await permission_service.assign_role_to_user(
                        user_id=regular_user.id,
                        role_id=user_role.id,
                        assigned_by="system"
                    )
                
                print(f"✅ Regular user created: {regular_user.email}")
            else:
                print("✅ Regular user already exists")
                
        finally:
            await db.close()
        
        print("\n🎉 Authentication system setup completed successfully!")
        print("\nDefault credentials:")
        print("  👑 Admin: admin@example.com / admin123")
        print("  👤 User:  user@example.com / user123")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("🚀 Knowledge Management Platform - Authentication Setup")
    print("=" * 60)
    
    # Run setup
    success = asyncio.run(setup_auth_system())
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nYou can now:")
        print("1. Start the server: python3 -m uvicorn app.main:app --reload")
        print("2. Access the API docs: http://localhost:8000/docs")
        print("3. Test authentication endpoints")
        
        # Ask if user wants to start the server
        try:
            start_server = input("\nWould you like to start the server now? (y/N): ").lower().strip()
            if start_server in ['y', 'yes']:
                print("\n🚀 Starting server...")
                subprocess.run([
                    sys.executable, "-m", "uvicorn", 
                    "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
                ])
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()