"""
Test script for new features: Knowledge Graph and Backup

Run this script to test the newly implemented features.
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

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.backup import BackupService
from app.models.knowledge import KnowledgeItem
from app.models.user import User
from sqlalchemy import select


async def test_knowledge_graph():
    """Test knowledge graph functionality."""
    print("\n" + "="*50)
    print("Testing Knowledge Graph Service")
    print("="*50)
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get first user
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No users found. Please run init_system.py first.")
            return
        
        print(f"✅ Found user: {user.username}")
        
        # Get knowledge items
        result = await session.execute(
            select(KnowledgeItem)
            .where(KnowledgeItem.author_id == user.id)
            .limit(5)
        )
        items = result.scalars().all()
        
        if len(items) < 2:
            print("⚠️  Need at least 2 knowledge items to test graph features.")
            print("   Please create some knowledge items first.")
            return
        
        print(f"✅ Found {len(items)} knowledge items")
        
        # Test graph service
        graph_service = KnowledgeGraphService(session)
        
        # Test 1: Create link
        try:
            link = await graph_service.create_link(
                source_id=items[0].id,
                target_id=items[1].id,
                user_id=user.id,
                link_type="related",
                description="Test link"
            )
            print(f"✅ Created link: {items[0].title} -> {items[1].title}")
        except Exception as e:
            print(f"⚠️  Link creation: {str(e)}")
        
        # Test 2: Get links
        try:
            links = await graph_service.get_links(items[0].id, user.id, "both")
            print(f"✅ Found {len(links)} links for item")
        except Exception as e:
            print(f"❌ Get links failed: {str(e)}")
        
        # Test 3: Get graph data
        try:
            graph_data = await graph_service.get_graph_data(user.id)
            print(f"✅ Graph data: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges")
        except Exception as e:
            print(f"❌ Get graph data failed: {str(e)}")
        
        # Test 4: Get graph stats
        try:
            stats = await graph_service.get_graph_stats(user.id)
            print(f"✅ Graph stats: {stats}")
        except Exception as e:
            print(f"❌ Get graph stats failed: {str(e)}")
        
        # Test 5: Detect related items
        try:
            related = await graph_service.detect_related_items(items[0].id, user.id, limit=5)
            print(f"✅ Found {len(related)} related items")
        except Exception as e:
            print(f"❌ Detect related items failed: {str(e)}")
    
    await engine.dispose()


async def test_backup():
    """Test backup functionality."""
    print("\n" + "="*50)
    print("Testing Backup Service")
    print("="*50)
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get first user
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No users found. Please run init_system.py first.")
            return
        
        print(f"✅ Found user: {user.username}")
        
        # Test backup service
        backup_service = BackupService(session)
        
        # Test 1: Create full backup
        try:
            backup_file = await backup_service.create_full_backup(user.id)
            backup_size = len(backup_file.getvalue())
            print(f"✅ Created full backup: {backup_size} bytes")
            
            # Test 2: Verify backup
            backup_file.seek(0)
            verification = await backup_service.verify_backup(backup_file)
            
            if verification['valid']:
                print(f"✅ Backup verification passed")
                print(f"   - Items: {verification.get('item_count', 0)}")
                print(f"   - Categories: {verification.get('category_count', 0)}")
                print(f"   - Tags: {verification.get('tag_count', 0)}")
            else:
                print(f"❌ Backup verification failed: {verification.get('error')}")
            
        except Exception as e:
            print(f"❌ Backup creation failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()


async def main():
    """Run all tests."""
    print("\n🧪 Testing New Features")
    print("="*50)
    
    try:
        await test_knowledge_graph()
        await test_backup()
        
        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
