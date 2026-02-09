#!/usr/bin/env python3
"""
Complete test of the authentication system implementation.
"""

import asyncio
import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_dir = project_root / "backend"

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["TESTING"] = "true"

# Set environment variables
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test_knowledge_platform.db'
os.environ['SECRET_KEY'] = 'test-secret-key-for-development'

async def test_complete_auth_system():
    """Test the complete authentication system."""
    
    print("🚀 Starting comprehensive authentication system test...")
    
    try:
        # Test 1: Import all modules
        print("\n📦 Testing imports...")
        
        from app.core.database import init_database, create_tables, get_db
        from app.services.auth import AuthService
        from app.services.permission import PermissionService, initialize_default_roles_and_permissions
        from app.schemas.auth import UserRegister
        from app.core.security import TokenManager, PasswordManager
        
        print("✅ All imports successful!")
        
        # Test 2: Initialize database
        print("\n📊 Initializing database...")
        await init_database()
        print("✅ Database initialized!")
        
        # Test 3: Create tables
        print("\n🏗️  Creating database tables...")
        await create_tables()
        print("✅ Tables created!")
        
        # Test 4: Initialize roles and permissions
        print("\n🔐 Initializing roles and permissions...")
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            await initialize_default_roles_and_permissions(db)
            print("✅ Roles and permissions initialized!")
            
            # Test 5: Create test user
            print("\n👤 Creating test user...")
            auth_service = AuthService(db)
            
            user_data = UserRegister(
                username="testadmin",
                email="admin@test.com",
                password="admin123",
                full_name="Test Administrator"
            )
            
            user = await auth_service.register_user(user_data)
            print(f"✅ User created: {user.username} ({user.email})")
            
            # Test 6: Assign admin role
            print("\n👑 Assigning admin role...")
            permission_service = PermissionService(db)
            
            admin_role = await permission_service.get_role_by_name("admin")
            if admin_role:
                await permission_service.assign_role_to_user(
                    user_id=user.id,
                    role_id=admin_role.id,
                    assigned_by="system"
                )
                print("✅ Admin role assigned!")
            
            # Test 7: Test authentication
            print("\n🔑 Testing authentication...")
            authenticated_user = await auth_service.authenticate_user("admin@test.com", "admin123")
            if authenticated_user:
                print("✅ Authentication successful!")
                
                # Test 8: Generate JWT token
                print("\n🎫 Testing JWT token generation...")
                token = TokenManager.create_access_token(
                    data={"sub": authenticated_user.id, "email": authenticated_user.email}
                )
                print("✅ JWT token generated!")
                
                # Test 9: Verify JWT token
                print("\n🔍 Testing JWT token verification...")
                payload = TokenManager.verify_token(token)
                if payload.get("sub") == authenticated_user.id:
                    print("✅ JWT token verification successful!")
                
                # Test 10: Test permissions
                print("\n🛡️  Testing permissions...")
                has_admin_permission = await permission_service.check_user_permission(
                    authenticated_user.id, "system.admin"
                )
                if has_admin_permission:
                    print("✅ Permission check successful!")
                
                # Test 11: Get user permissions
                print("\n📋 Getting user permissions...")
                permissions = await permission_service.get_user_permissions(authenticated_user.id)
                print(f"✅ User has {len(permissions)} permissions")
                
                # Test 12: Password hashing
                print("\n🔒 Testing password security...")
                test_password = "testpassword123"
                hashed = PasswordManager.hash_password(test_password)
                is_valid = PasswordManager.verify_password(test_password, hashed)
                if is_valid:
                    print("✅ Password hashing and verification successful!")
                
            else:
                print("❌ Authentication failed!")
                return False
                
        finally:
            await db.close()
        
        print("\n🎉 All authentication system tests passed successfully!")
        print("\nSystem is ready for use with the following test credentials:")
        print("  📧 Email: admin@test.com")
        print("  🔑 Password: admin123")
        print("  👑 Role: Administrator")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Authentication system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_auth_system())
    sys.exit(0 if success else 1)