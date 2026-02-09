"""
Simple test script for knowledge service.
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.user import User
from app.models.knowledge import KnowledgeItem
from app.services.knowledge import KnowledgeService
from app.schemas.knowledge import KnowledgeCreate
from app.core.security import PasswordManager
from app.core.database import Base


async def test_knowledge_service():
    """Test knowledge service operations."""
    
    # Create test database
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test_knowledge_simple.db",
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        # Create test user (without password hashing to avoid bcrypt issues)
        user = User(
            id=str(uuid.uuid4()),
            username="testuser",
            email="test@example.com",
            password_hash="dummy_hash",  # Skip actual hashing for this test
            is_active=True
        )
        session.add(user)
        await session.commit()
        
        print(f"✓ Created test user: {user.id}")
        
        # Test create knowledge item
        service = KnowledgeService(session)
        
        create_data = KnowledgeCreate(
            title="Test Knowledge Item",
            content="This is a test content with multiple words to test word count calculation.",
            content_type="markdown",
            summary="Test summary",
            visibility="private",
            is_published=False
        )
        
        item = await service.create_knowledge_item(user.id, create_data)
        print(f"✓ Created knowledge item: {item.id}")
        print(f"  - Title: {item.title}")
        print(f"  - Word count: {item.word_count}")
        print(f"  - Reading time: {item.reading_time} min")
        print(f"  - Versions: {len(item.versions)}")
        
        # Test get knowledge item
        retrieved_item = await service.get_knowledge_item(item.id, user.id)
        print(f"✓ Retrieved knowledge item: {retrieved_item.id}")
        print(f"  - View count: {retrieved_item.view_count}")
        
        # Test update knowledge item
        from app.schemas.knowledge import KnowledgeUpdate
        
        update_data = KnowledgeUpdate(
            title="Updated Title",
            content="Updated content with even more words for testing",
            change_summary="Updated title and content"
        )
        
        updated_item = await service.update_knowledge_item(item.id, user.id, update_data)
        print(f"✓ Updated knowledge item: {updated_item.id}")
        print(f"  - New title: {updated_item.title}")
        print(f"  - New word count: {updated_item.word_count}")
        print(f"  - Versions: {len(updated_item.versions)}")
        
        # Test publish
        published_item = await service.publish_knowledge_item(item.id, user.id)
        print(f"✓ Published knowledge item: {published_item.id}")
        print(f"  - Is published: {published_item.is_published}")
        print(f"  - Published at: {published_item.published_at}")
        
        # Test delete
        deleted_item = await service.delete_knowledge_item(item.id, user.id)
        print(f"✓ Deleted knowledge item: {deleted_item.id}")
        print(f"  - Is deleted: {deleted_item.is_deleted}")
        print(f"  - Is recoverable: {deleted_item.is_recoverable}")
        print(f"  - Days until permanent deletion: {deleted_item.days_until_permanent_deletion}")
        
        # Test restore
        restored_item = await service.restore_knowledge_item(item.id, user.id)
        print(f"✓ Restored knowledge item: {restored_item.id}")
        print(f"  - Is deleted: {restored_item.is_deleted}")
        
        # Test list
        from app.schemas.knowledge import KnowledgeFilter
        
        filters = KnowledgeFilter(page=1, page_size=20)
        result = await service.list_knowledge_items(user.id, filters)
        print(f"✓ Listed knowledge items:")
        print(f"  - Total: {result.total}")
        print(f"  - Items: {len(result.items)}")
        
        print("\n✅ All tests passed!")
    
    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_knowledge_service())
