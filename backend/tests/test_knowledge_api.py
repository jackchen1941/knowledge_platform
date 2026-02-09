"""
Tests for Knowledge API endpoints.
"""

import pytest
import uuid
from datetime import datetime

from app.models.user import User
from app.models.knowledge import KnowledgeItem
from app.models.category import Category
from app.models.tag import Tag
from app.core.security import PasswordManager, TokenManager


@pytest.mark.asyncio
async def test_create_knowledge_item(client, db_session):
    """Test creating a knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Create knowledge item
    response = await client.post(
        "/api/v1/knowledge",
        json={
            "title": "Test Knowledge Item",
            "content": "This is test content for the knowledge item.",
            "content_type": "markdown",
            "summary": "Test summary",
            "visibility": "private",
            "is_published": False
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Knowledge Item"
    assert data["content"] == "This is test content for the knowledge item."
    assert data["author_id"] == user.id
    assert data["is_published"] == False
    assert data["word_count"] > 0
    assert data["reading_time"] > 0


@pytest.mark.asyncio
async def test_get_knowledge_item(client, db_session):
    """Test getting a knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create a knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Test Item",
        content="Test content",
        content_type="markdown",
        author_id=user.id,
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Get knowledge item
    response = await client.get(
        f"/api/v1/knowledge/{item.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item.id
    assert data["title"] == "Test Item"
    assert data["view_count"] == 1  # Should increment


@pytest.mark.asyncio
async def test_list_knowledge_items(client, db_session):
    """Test listing knowledge items."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create multiple knowledge items
    for i in range(5):
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title=f"Test Item {i}",
            content=f"Test content {i}",
            content_type="markdown",
            author_id=user.id,
            word_count=2,
            reading_time=1
        )
        db_session.add(item)
    
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # List knowledge items
    response = await client.get(
        "/api/v1/knowledge",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_update_knowledge_item(client, db_session):
    """Test updating a knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create a knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Original Title",
        content="Original content",
        content_type="markdown",
        author_id=user.id,
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Update knowledge item
    response = await client.put(
        f"/api/v1/knowledge/{item.id}",
        json={
            "title": "Updated Title",
            "content": "Updated content with more words",
            "change_summary": "Updated title and content"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content with more words"
    assert data["word_count"] == 5


@pytest.mark.asyncio
async def test_save_draft(client, db_session):
    """Test saving a draft."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create a knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Draft Item",
        content="Draft content",
        content_type="markdown",
        author_id=user.id,
        is_published=True,
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Save draft
    response = await client.post(
        f"/api/v1/knowledge/{item.id}/draft",
        json={
            "title": "Draft Title Updated",
            "content": "Draft content updated"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Draft Title Updated"
    assert data["is_published"] == False  # Should be unpublished


@pytest.mark.asyncio
async def test_publish_knowledge_item(client, db_session):
    """Test publishing a knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create an unpublished knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Unpublished Item",
        content="Unpublished content",
        content_type="markdown",
        author_id=user.id,
        is_published=False,
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Publish knowledge item
    response = await client.post(
        f"/api/v1/knowledge/{item.id}/publish",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_published"] == True
    assert data["published_at"] is not None


@pytest.mark.asyncio
async def test_delete_knowledge_item(client, db_session):
    """Test soft deleting a knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create a knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Item to Delete",
        content="Content to delete",
        content_type="markdown",
        author_id=user.id,
        word_count=3,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Delete knowledge item
    response = await client.delete(
        f"/api/v1/knowledge/{item.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_deleted"] == True
    assert data["deleted_at"] is not None
    assert data["is_recoverable"] == True


@pytest.mark.asyncio
async def test_restore_knowledge_item(client, db_session):
    """Test restoring a soft-deleted knowledge item."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create a deleted knowledge item
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Deleted Item",
        content="Deleted content",
        content_type="markdown",
        author_id=user.id,
        is_deleted=True,
        deleted_at=datetime.utcnow(),
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Restore knowledge item
    response = await client.post(
        f"/api/v1/knowledge/{item.id}/restore",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_deleted"] == False
    assert data["deleted_at"] is None


@pytest.mark.asyncio
async def test_get_deleted_items(client, db_session):
    """Test getting deleted items (recycle bin)."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create deleted items
    for i in range(3):
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title=f"Deleted Item {i}",
            content=f"Deleted content {i}",
            content_type="markdown",
            author_id=user.id,
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            word_count=2,
            reading_time=1
        )
        db_session.add(item)
    
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Get deleted items
    response = await client.get(
        "/api/v1/knowledge/deleted",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_search_knowledge_items(client, db_session):
    """Test searching knowledge items."""
    
    # Create a test user
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user)
    
    # Create knowledge items with different content
    item1 = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Python Programming",
        content="Learn Python programming language",
        content_type="markdown",
        author_id=user.id,
        word_count=4,
        reading_time=1
    )
    item2 = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="JavaScript Guide",
        content="Learn JavaScript for web development",
        content_type="markdown",
        author_id=user.id,
        word_count=5,
        reading_time=1
    )
    db_session.add(item1)
    db_session.add(item2)
    await db_session.commit()
    
    # Create access token
    token = TokenManager.create_access_token({"sub": user.id, "email": user.email})
    
    # Search for Python
    response = await client.get(
        "/api/v1/knowledge/search?q=Python",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Programming"


@pytest.mark.asyncio
async def test_permission_check(client, db_session):
    """Test that users cannot access private items from other users."""
    
    # Create two users
    user1 = User(
        id=str(uuid.uuid4()),
        username="user1",
        email="user1@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    user2 = User(
        id=str(uuid.uuid4()),
        username="user2",
        email="user2@example.com",
        password_hash=PasswordManager.hash_password("password123"),
        is_active=True
    )
    db_session.add(user1)
    db_session.add(user2)
    
    # Create a private item for user1
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Private Item",
        content="Private content",
        content_type="markdown",
        author_id=user1.id,
        visibility="private",
        word_count=2,
        reading_time=1
    )
    db_session.add(item)
    await db_session.commit()
    
    # Create access token for user2
    token = TokenManager.create_access_token({"sub": user2.id, "email": user2.email})
    
    # Try to access user1's private item as user2
    response = await client.get(
        f"/api/v1/knowledge/{item.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403  # Forbidden
