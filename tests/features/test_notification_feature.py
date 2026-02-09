#!/usr/bin/env python3
"""
Test script for notification feature functionality
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

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.user import User
from app.models.notification import Notification, NotificationTemplate, NotificationPreference

settings = get_settings()


def test_notification_functionality():
    """Test notification functionality"""
    print("🔔 Testing Notification Feature Functionality")
    print("=" * 50)
    
    # Create synchronous database connection
    sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    engine = create_engine(sync_db_url, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test 1: Check if notification tables exist
        print("\n1. Checking notification tables...")
        
        # Test Notification table
        notification_count = db.query(Notification).count()
        print(f"   ✅ Notification table exists - {notification_count} records")
        
        # Test NotificationTemplate table
        template_count = db.query(NotificationTemplate).count()
        print(f"   ✅ NotificationTemplate table exists - {template_count} records")
        
        # Test NotificationPreference table
        preference_count = db.query(NotificationPreference).count()
        print(f"   ✅ NotificationPreference table exists - {preference_count} records")
        
        # Test 2: Get test user
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
        
        # Test 3: Create a notification
        print("\n3. Testing notification creation...")
        
        # Check if notification already exists
        existing_notification = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.title == "Test Notification"
        ).first()
        
        if existing_notification:
            notification = existing_notification
            print(f"   ✅ Using existing notification: {notification.title}")
        else:
            notification = Notification(
                user_id=test_user.id,
                title="Test Notification",
                message="This is a test notification for the notification system.",
                notification_type="info",
                category="system",
                priority="normal"
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            print(f"   ✅ Notification created: {notification.title} (ID: {notification.id})")
        
        # Test 4: Create a notification template
        print("\n4. Testing notification template...")
        
        existing_template = db.query(NotificationTemplate).filter(
            NotificationTemplate.template_key == "sync_completed"
        ).first()
        
        if existing_template:
            template = existing_template
            print(f"   ✅ Using existing template: {template.name}")
        else:
            template = NotificationTemplate(
                template_key="sync_completed",
                name="Sync Completed Template",
                description="Template for sync completion notifications",
                title_template="同步完成",
                message_template="设备 {device_name} 同步完成，处理了 {changes_count} 个变更。",
                notification_type="success",
                category="sync",
                default_priority="normal",
                default_expires_hours=24,
                variables=["device_name", "changes_count"]
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            print(f"   ✅ Template created: {template.name} (Key: {template.template_key})")
        
        # Test 5: Create notification preferences
        print("\n5. Testing notification preferences...")
        
        existing_pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == test_user.id,
            NotificationPreference.category == "sync"
        ).first()
        
        if existing_pref:
            preference = existing_pref
            print(f"   ✅ Using existing preference for category: {preference.category}")
        else:
            preference = NotificationPreference(
                user_id=test_user.id,
                category="sync",
                enabled=True,
                in_app=True,
                email=False,
                push=False,
                min_priority="normal"
            )
            db.add(preference)
            db.commit()
            db.refresh(preference)
            print(f"   ✅ Preference created for category: {preference.category}")
        
        # Test 6: Query notification data
        print("\n6. Testing notification queries...")
        
        # Count notifications for user
        user_notifications = db.query(Notification).filter(Notification.user_id == test_user.id).count()
        print(f"   ✅ User has {user_notifications} notification(s)")
        
        # Count unread notifications
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.is_read == False
        ).count()
        print(f"   ✅ User has {unread_notifications} unread notification(s)")
        
        # Count templates
        total_templates = db.query(NotificationTemplate).count()
        print(f"   ✅ System has {total_templates} notification template(s)")
        
        # Test 7: Test notification properties
        print("\n7. Testing notification properties...")
        
        # Test expiration
        print(f"   ✅ Notification expired: {notification.is_expired}")
        print(f"   ✅ Notification scheduled: {notification.is_scheduled}")
        
        # Test template variables
        print(f"   ✅ Template variables: {template.variables}")
        
        # Test preference settings
        print(f"   ✅ Preference enabled: {preference.enabled}")
        print(f"   ✅ In-app notifications: {preference.in_app}")
        
        print("\n" + "=" * 50)
        print("✅ All notification functionality tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = test_notification_functionality()
    sys.exit(0 if success else 1)