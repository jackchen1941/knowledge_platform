#!/usr/bin/env python3
"""
Test script for sync feature functionality
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
backend_dir = project_root / "backend"

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Set environment variables
os.environ["TESTING"] = "true"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.user import User
from app.models.sync import SyncDevice, SyncChange
from app.core.database import Base

settings = get_settings()


def test_sync_functionality():
    """Test basic sync functionality"""
    print("🔄 Testing Sync Feature Functionality")
    print("=" * 50)
    
    # Create synchronous database connection
    # Convert async URL to sync URL
    sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    engine = create_engine(sync_db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test 1: Check if sync tables exist
        print("\n1. Checking sync tables...")
        
        # Test SyncDevice table
        device_count = db.query(SyncDevice).count()
        print(f"   ✅ SyncDevice table exists - {device_count} records")
        
        # Test SyncChange table  
        change_count = db.query(SyncChange).count()
        print(f"   ✅ SyncChange table exists - {change_count} records")
        
        # Test 2: Get or create a test user
        print("\n2. Setting up test user...")
        test_user = db.query(User).filter(User.username == "test_user").first()
        if not test_user:
            print("   Creating test user...")
            test_user = User(
                username="test_user",
                email="test@example.com",
                password_hash="dummy_hash",
                full_name="Test User"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        print(f"   ✅ Test user: {test_user.username} (ID: {test_user.id})")
        
        # Test 3: Create a sync device
        print("\n3. Testing device creation...")
        
        # Check if device already exists
        existing_device = db.query(SyncDevice).filter(
            SyncDevice.user_id == test_user.id,
            SyncDevice.device_name == "Test Device"
        ).first()
        
        if existing_device:
            device = existing_device
            print(f"   ✅ Using existing device: {device.device_name}")
        else:
            device = SyncDevice(
                user_id=test_user.id,
                device_name="Test Device",
                device_type="desktop",
                device_id="test-device-001",
                is_active=True
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            print(f"   ✅ Device created: {device.device_name} (ID: {device.id})")
        
        # Test 4: Create a sync change
        print("\n4. Testing sync change creation...")
        change = SyncChange(
            user_id=test_user.id,
            device_id=device.id,
            entity_type="knowledge_item",
            entity_id="test-knowledge-1",
            operation="create",
            change_data={
                "title": "Test Knowledge Item",
                "content": "This is a test knowledge item for sync testing"
            },
            timestamp=datetime.utcnow()
        )
        db.add(change)
        db.commit()
        db.refresh(change)
        print(f"   ✅ Change created: {change.operation} on {change.entity_type}")
        
        # Test 5: Query sync data
        print("\n5. Testing sync data queries...")
        
        # Count devices for user
        user_devices = db.query(SyncDevice).filter(SyncDevice.user_id == test_user.id).count()
        print(f"   ✅ User has {user_devices} device(s)")
        
        # Count changes for user
        user_changes = db.query(SyncChange).filter(SyncChange.user_id == test_user.id).count()
        print(f"   ✅ User has {user_changes} change(s)")
        
        # Test 6: Test relationships
        print("\n6. Testing model relationships...")
        
        # Test user -> devices relationship
        if hasattr(test_user, 'sync_devices'):
            devices_via_relationship = len(test_user.sync_devices)
            print(f"   ✅ User.sync_devices relationship works: {devices_via_relationship} device(s)")
        else:
            print("   ⚠️  User.sync_devices relationship not found")
        
        # Test device -> user relationship
        if hasattr(device, 'user'):
            device_user = device.user
            print(f"   ✅ Device.user relationship works: {device_user.username if device_user else 'None'}")
        else:
            print("   ⚠️  Device.user relationship not found")
        
        print("\n" + "=" * 50)
        print("✅ All sync functionality tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = test_sync_functionality()
    sys.exit(0 if success else 1)