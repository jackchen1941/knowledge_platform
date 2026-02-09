#!/usr/bin/env python3
"""
Simple startup test - test core components without complex imports
"""

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
os.environ["DATABASE_URL"] = "sqlite:///./test_knowledge_platform.db"

def test_basic_imports():
    """Test basic imports step by step"""
    print("🔄 Testing Basic Imports")
    print("=" * 40)
    
    try:
        print("1. Testing core config...")
        from app.core.config import get_settings
        settings = get_settings()
        print(f"   ✅ Config loaded: {settings.APP_NAME}")
        
        print("2. Testing database...")
        from app.core.database import Base
        print("   ✅ Database base imported")
        
        print("3. Testing basic models...")
        from app.models.user import User
        print("   ✅ User model imported")
        
        from app.models.sync import SyncDevice, SyncChange
        print("   ✅ Sync models imported")
        
        print("4. Testing security...")
        from app.core.security import pwd_context, TokenManager
        print("   ✅ Security components imported")
        
        print("5. Testing sync service...")
        from app.services.sync import SyncService
        print("   ✅ Sync service imported")
        
        print("\n" + "=" * 40)
        print("✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔄 Testing Database Connection")
    print("=" * 40)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Convert async URL to sync URL for testing
        sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
        engine = create_engine(sync_db_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection
        from sqlalchemy import text
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        print(f"   ✅ Database connection successful: {result[0]}")
        return True
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Knowledge Platform - Simple Startup Test")
    print("=" * 50)
    
    success = True
    
    # Test basic imports
    if not test_basic_imports():
        success = False
    
    # Test database connection
    if not test_database_connection():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Core system is working.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    sys.exit(0 if success else 1)