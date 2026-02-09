"""
Test Knowledge Models

Unit tests for knowledge management models including KnowledgeItem, Category, Tag, 
Attachment, and version control functionality.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models import (
    User, KnowledgeItem, KnowledgeVersion, Category, Tag, 
    Attachment, KnowledgeLink
)


# Fixtures
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestKnowledgeItem:
    """Test KnowledgeItem model functionality."""
    
    @pytest.mark.asyncio
    async def test_create_knowledge_item(self, db_session: AsyncSession, test_user: User):
        """Test creating a basic knowledge item."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Test Article",
            content="# Test Content\n\nThis is a test article.",
            content_type="markdown",
            author_id=test_user.id,
            is_published=True,
            is_deleted=False,
            visibility="private"
        )
        
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)
        
        assert item.id is not None
        assert item.title == "Test Article"
        assert item.author_id == test_user.id
        assert item.is_deleted is False
        assert item.deleted_at is None
    
    @pytest.mark.asyncio
    async def test_soft_delete(self, db_session: AsyncSession, test_user: User):
        """Test soft delete functionality."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="To Be Deleted",
            content="Content to delete",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Soft delete the item
        item.soft_delete()
        await db_session.commit()
        await db_session.refresh(item)
        
        assert item.is_deleted is True
        assert item.deleted_at is not None
        assert item.is_recoverable is True
    
    @pytest.mark.asyncio
    async def test_restore_deleted_item(self, db_session: AsyncSession, test_user: User):
        """Test restoring a soft-deleted item."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Restored Item",
            content="Content to restore",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Soft delete and then restore
        item.soft_delete()
        await db_session.commit()
        
        item.restore()
        await db_session.commit()
        await db_session.refresh(item)
        
        assert item.is_deleted is False
        assert item.deleted_at is None
        assert item.is_recoverable is False
    
    @pytest.mark.asyncio
    async def test_is_recoverable_within_30_days(self, db_session: AsyncSession, test_user: User):
        """Test that items deleted within 30 days are recoverable."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Recent Delete",
            content="Recently deleted content",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Delete 15 days ago
        item.is_deleted = True
        item.deleted_at = datetime.utcnow() - timedelta(days=15)
        await db_session.commit()
        await db_session.refresh(item)
        
        assert item.is_recoverable is True
        assert item.days_until_permanent_deletion == 15
    
    @pytest.mark.asyncio
    async def test_not_recoverable_after_30_days(self, db_session: AsyncSession, test_user: User):
        """Test that items deleted more than 30 days ago are not recoverable."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Old Delete",
            content="Old deleted content",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Delete 31 days ago
        item.is_deleted = True
        item.deleted_at = datetime.utcnow() - timedelta(days=31)
        await db_session.commit()
        await db_session.refresh(item)
        
        assert item.is_recoverable is False
        assert item.days_until_permanent_deletion == 0


class TestKnowledgeVersion:
    """Test version control functionality."""
    
    @pytest.mark.asyncio
    async def test_create_version(self, db_session: AsyncSession, test_user: User):
        """Test creating a version snapshot."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Versioned Article",
            content="Original content",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Create a version
        version = item.create_version(
            user_id=test_user.id,
            change_summary="Initial version",
            change_type="create"
        )
        
        db_session.add(version)
        await db_session.commit()
        await db_session.refresh(version)
        
        assert version.id is not None
        assert version.knowledge_item_id == item.id
        assert version.version_number == 1
        assert version.title == item.title
        assert version.content == item.content
        assert version.change_summary == "Initial version"
    
    @pytest.mark.asyncio
    async def test_multiple_versions(self, db_session: AsyncSession, test_user: User):
        """Test creating multiple versions."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Multi-Version Article",
            content="Version 1 content",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        # Create first version
        v1 = item.create_version(test_user.id, "Version 1", "create")
        db_session.add(v1)
        await db_session.commit()
        
        # Update content and create second version
        item.content = "Version 2 content"
        v2 = item.create_version(test_user.id, "Version 2", "edit")
        db_session.add(v2)
        await db_session.commit()
        
        # Update content and create third version
        item.content = "Version 3 content"
        v3 = item.create_version(test_user.id, "Version 3", "edit")
        db_session.add(v3)
        await db_session.commit()
        
        await db_session.refresh(item)
        
        assert len(item.versions) == 3
        assert item.versions[0].version_number == 1
        assert item.versions[1].version_number == 2
        assert item.versions[2].version_number == 3


class TestCategory:
    """Test Category model functionality."""
    
    @pytest.mark.asyncio
    async def test_create_category(self, db_session: AsyncSession, test_user: User):
        """Test creating a basic category."""
        category = Category(
            id=str(uuid.uuid4()),
            name="Programming",
            description="Programming related articles",
            user_id=test_user.id,
            color="#3498db",
            icon="code"
        )
        
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Programming"
        assert category.depth == 0
        assert category.full_path == "Programming"
    
    @pytest.mark.asyncio
    async def test_hierarchical_categories(self, db_session: AsyncSession, test_user: User):
        """Test creating hierarchical categories."""
        parent = Category(
            id=str(uuid.uuid4()),
            name="Technology",
            user_id=test_user.id
        )
        
        db_session.add(parent)
        await db_session.commit()
        
        child = Category(
            id=str(uuid.uuid4()),
            name="Python",
            user_id=test_user.id,
            parent_id=parent.id
        )
        
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)
        
        assert child.parent_id == parent.id
        assert child.depth == 1
        assert child.full_path == "Technology > Python"
    
    @pytest.mark.asyncio
    async def test_get_ancestors(self, db_session: AsyncSession, test_user: User):
        """Test getting ancestor categories."""
        root = Category(id=str(uuid.uuid4()), name="Root", user_id=test_user.id)
        db_session.add(root)
        await db_session.commit()
        
        level1 = Category(id=str(uuid.uuid4()), name="Level1", user_id=test_user.id, parent_id=root.id)
        db_session.add(level1)
        await db_session.commit()
        
        level2 = Category(id=str(uuid.uuid4()), name="Level2", user_id=test_user.id, parent_id=level1.id)
        db_session.add(level2)
        await db_session.commit()
        await db_session.refresh(level2)
        
        ancestors = level2.get_ancestors()
        assert len(ancestors) == 2
        assert ancestors[0].name == "Root"
        assert ancestors[1].name == "Level1"
    
    @pytest.mark.asyncio
    async def test_get_descendants(self, db_session: AsyncSession, test_user: User):
        """Test getting descendant categories."""
        root = Category(id=str(uuid.uuid4()), name="Root", user_id=test_user.id)
        db_session.add(root)
        await db_session.commit()
        
        child1 = Category(id=str(uuid.uuid4()), name="Child1", user_id=test_user.id, parent_id=root.id)
        child2 = Category(id=str(uuid.uuid4()), name="Child2", user_id=test_user.id, parent_id=root.id)
        db_session.add_all([child1, child2])
        await db_session.commit()
        
        grandchild = Category(id=str(uuid.uuid4()), name="Grandchild", user_id=test_user.id, parent_id=child1.id)
        db_session.add(grandchild)
        await db_session.commit()
        await db_session.refresh(root)
        
        descendants = root.get_descendants()
        assert len(descendants) == 3


class TestTag:
    """Test Tag model functionality."""
    
    @pytest.mark.asyncio
    async def test_create_tag(self, db_session: AsyncSession, test_user: User):
        """Test creating a basic tag."""
        tag = Tag(
            id=str(uuid.uuid4()),
            name="python",
            description="Python programming language",
            user_id=test_user.id,
            color="#3776ab"
        )
        
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)
        
        assert tag.id is not None
        assert tag.name == "python"
        assert tag.usage_count == 0
    
    @pytest.mark.asyncio
    async def test_tag_usage_count(self, db_session: AsyncSession, test_user: User):
        """Test incrementing and decrementing tag usage count."""
        tag = Tag(
            id=str(uuid.uuid4()),
            name="test-tag",
            user_id=test_user.id
        )
        
        db_session.add(tag)
        await db_session.commit()
        
        # Increment usage
        tag.increment_usage()
        await db_session.commit()
        await db_session.refresh(tag)
        assert tag.usage_count == 1
        
        # Increment again
        tag.increment_usage()
        await db_session.commit()
        await db_session.refresh(tag)
        assert tag.usage_count == 2
        
        # Decrement
        tag.decrement_usage()
        await db_session.commit()
        await db_session.refresh(tag)
        assert tag.usage_count == 1
    
    @pytest.mark.asyncio
    async def test_tag_knowledge_item_relationship(self, db_session: AsyncSession, test_user: User):
        """Test many-to-many relationship between tags and knowledge items."""
        tag1 = Tag(id=str(uuid.uuid4()), name="tag1", user_id=test_user.id)
        tag2 = Tag(id=str(uuid.uuid4()), name="tag2", user_id=test_user.id)
        
        db_session.add_all([tag1, tag2])
        await db_session.commit()
        
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Tagged Article",
            content="Content with tags",
            content_type="markdown",
            author_id=test_user.id
        )
        
        item.tags.append(tag1)
        item.tags.append(tag2)
        
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)
        
        assert len(item.tags) == 2
        assert tag1 in item.tags
        assert tag2 in item.tags


class TestAttachment:
    """Test Attachment model functionality."""
    
    @pytest.mark.asyncio
    async def test_create_attachment(self, db_session: AsyncSession, test_user: User):
        """Test creating an attachment."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Article with Attachment",
            content="Content",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add(item)
        await db_session.commit()
        
        attachment = Attachment(
            id=str(uuid.uuid4()),
            filename="test_image.jpg",
            original_filename="test_image.jpg",
            file_path="/uploads/test_image.jpg",
            mime_type="image/jpeg",
            file_size=1024000,  # 1MB
            knowledge_item_id=item.id,
            uploaded_by=test_user.id
        )
        
        db_session.add(attachment)
        await db_session.commit()
        await db_session.refresh(attachment)
        
        assert attachment.id is not None
        assert attachment.knowledge_item_id == item.id
        assert attachment.is_image is True
        assert attachment.file_size_human == "1000.0 KB"
    
    @pytest.mark.asyncio
    async def test_attachment_type_detection(self, db_session: AsyncSession, test_user: User):
        """Test attachment type detection methods."""
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Test",
            content="Test",
            content_type="markdown",
            author_id=test_user.id
        )
        db_session.add(item)
        await db_session.commit()
        
        # Test image
        image = Attachment(
            id=str(uuid.uuid4()),
            filename="image.png",
            original_filename="image.png",
            file_path="/uploads/image.png",
            mime_type="image/png",
            file_size=1024,
            knowledge_item_id=item.id,
            uploaded_by=test_user.id
        )
        assert image.is_image is True
        assert image.is_video is False
        
        # Test video
        video = Attachment(
            id=str(uuid.uuid4()),
            filename="video.mp4",
            original_filename="video.mp4",
            file_path="/uploads/video.mp4",
            mime_type="video/mp4",
            file_size=1024,
            knowledge_item_id=item.id,
            uploaded_by=test_user.id
        )
        assert video.is_video is True
        assert video.is_image is False
        
        # Test document
        doc = Attachment(
            id=str(uuid.uuid4()),
            filename="doc.pdf",
            original_filename="doc.pdf",
            file_path="/uploads/doc.pdf",
            mime_type="application/pdf",
            file_size=1024,
            knowledge_item_id=item.id,
            uploaded_by=test_user.id
        )
        assert doc.is_document is True
        assert doc.is_image is False


class TestKnowledgeLink:
    """Test KnowledgeLink model for knowledge graph."""
    
    @pytest.mark.asyncio
    async def test_create_knowledge_link(self, db_session: AsyncSession, test_user: User):
        """Test creating a link between knowledge items."""
        item1 = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Article 1",
            content="Content 1",
            content_type="markdown",
            author_id=test_user.id
        )
        
        item2 = KnowledgeItem(
            id=str(uuid.uuid4()),
            title="Article 2",
            content="Content 2",
            content_type="markdown",
            author_id=test_user.id
        )
        
        db_session.add_all([item1, item2])
        await db_session.commit()
        
        link = KnowledgeLink(
            id=str(uuid.uuid4()),
            from_item_id=item1.id,
            to_item_id=item2.id,
            link_type="reference",
            description="Article 1 references Article 2",
            created_by=test_user.id
        )
        
        db_session.add(link)
        await db_session.commit()
        await db_session.refresh(link)
        
        assert link.id is not None
        assert link.from_item_id == item1.id
        assert link.to_item_id == item2.id
        assert link.link_type == "reference"
