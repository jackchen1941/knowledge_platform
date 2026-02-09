#!/usr/bin/env python3
"""
Quick system test to verify the knowledge management platform is working.
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

async def test_system():
    """Test basic system functionality."""
    print("🧪 Testing Knowledge Management Platform\n")
    
    try:
        # Test 1: Import core modules
        print("1️⃣ Testing imports...")
        from app.core.database import init_database
        from app.models.user import User
        from app.models.knowledge import KnowledgeItem
        from app.services.auth import AuthService
        from app.services.knowledge import KnowledgeService
        print("   ✅ All imports successful\n")
        
        # Test 2: Database connection
        print("2️⃣ Testing database connection...")
        await init_database()
        print("   ✅ Database connection successful\n")
        
        # Test 3: Check models
        print("3️⃣ Checking data models...")
        print(f"   - User model: {User.__tablename__}")
        print(f"   - KnowledgeItem model: {KnowledgeItem.__tablename__}")
        print("   ✅ Models loaded successfully\n")
        
        print("✅ All basic tests passed!")
        print("\n📝 System is ready to use!")
        print("\nNext steps:")
        print("1. Start the backend server:")
        print("   cd backend && python3 -m uvicorn app.main:app --reload")
        print("\n2. Access API docs:")
        print("   http://localhost:8000/docs")
        print("\n3. Test authentication:")
        print("   - Register a user")
        print("   - Login to get JWT token")
        print("   - Create knowledge items")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_system())
    sys.exit(0 if success else 1)
