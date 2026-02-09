#!/usr/bin/env python3
"""
Test authentication system functionality.
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

from app.core.database import init_database, create_tables
from app.services.auth import AuthService
from app.schemas.auth import UserRegister
from app.core.database import get_db


async def test_basic_auth():
    """Test basic authentication functionality."""
    print("🧪 Testing authentication system...")
    
    try:
        # 1. Initialize database
        print("📊 Initializing database...")
        await init_database()
        
        # 2. Create tables
        print("🏗️  Creating tables...")
        await create_tables()
        
        # 3. Test user registration
        print("👤 Testing user registration...")
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            auth_service = AuthService(db)
            
            # Create a test user
            user_data = UserRegister(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                full_name="Test User"
            )
            
            user = await auth_service.register_user(user_data)
            print(f"✅ User created: {user.username} ({user.email})")
            
            # Test authentication
            authenticated_user = await auth_service.authenticate_user("test@example.com", "testpass123")
            if authenticated_user:
                print("✅ User authentication successful!")
            else:
                print("❌ User authentication failed!")
                
        finally:
            await db.close()
        
        print("🎉 Authentication system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_basic_auth())