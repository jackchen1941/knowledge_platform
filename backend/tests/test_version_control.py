"""
Tests for Version Control and History Management

Tests for version control API endpoints including:
- Getting version list
- Getting specific version
- Restoring to a version
- Comparing versions
- Deleting versions
- Cleaning up old versions
"""

import pytest
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.knowledge import KnowledgeItem, KnowledgeVersion
from app.core.security import create_access_token


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id="test-user-version",
        username="versionuser",
        email="version@test.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_knowledge_item(db_session: AsyncSession, test_user: User) -> KnowledgeItem:
    """Create a test knowledge item with multiple versions."""
    import uuid
    
    item = KnowledgeItem(
        id=str(uuid.uuid4()),
        title="Test Article",
        content="Initial content",
        content_type="markdown",
        author_id=test_user.id,
        is_published=True,
        visibility="private",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(item)
    
    # Create initial version
    version1 = KnowledgeVersion(
        id=str(uuid.uuid4()),
        knowledge_item_id=item.id,
        version_number=1,
        title="Test Article",
        content="Initial content",
        content_type="markdown",
        change_summary="Initial creation",
        change_type="create",
        created_by=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(version1)
    
    # Create second version
    version2 = KnowledgeVersion(
        id=str(uuid.uuid4()),
        knowledge_item_id=item.id,
        version_number=2,
        title="Test Article Updated",
        content="Updated content with more details",
        content_type="markdown",
        change_summary="Added more details",
        change_type="edit",
        created_by=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(version2)
    
    # Create third version
    version3 = KnowledgeVersion(
        id=str(uuid.uuid4()),
        knowledge_item_id=item.id,
        version_number=3,
        title="Test Article Final",
        content="Final content with complete information",
        content_type="markdown",
        change_summary="Finalized content",
        change_type="edit",
        created_by=test_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(version3)
    
    await db_session.commit()
    await db_session.refresh(item)
    
    return item


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


class TestGetVersions:
    """Tests for getting version list."""
    
    async def test_get_versions_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict
    ):
        """Test getting all versions of a knowledge item."""
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "versions" in data
        assert "total" in data
        assert "knowledge_item_id" in data
        assert data["knowledge_item_id"] == test_knowledge_item.id
        assert data["total"] == 3
        assert len(data["versions"]) == 3
        
        # Check versions are ordered by version_number descending
        assert data["versions"][0]["version_number"] == 3
        assert data["versions"][1]["version_number"] == 2
        assert data["versions"][2]["version_number"] == 1
        
        # Check version structure
        version = data["versions"][0]
        assert "id" in version
        assert "version_number" in version
        assert "title" in version
        assert "change_summary" in version
        assert "change_type" in version
        assert "created_by" in version
        assert "created_at" in version
        assert "content_preview" in version
    
    async def test_get_versions_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting versions for non-existent item."""
        response = await client.get(
            "/api/v1/knowledge/non-existent-id/versions",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_versions_unauthorized(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem
    ):
        """Test getting versions without authentication."""
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions"
        )
        
        assert response.status_code == 403


class TestGetSpecificVersion:
    """Tests for getting a specific version."""
    
    async def test_get_version_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test getting a specific version by ID."""
        # Get the first version
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 1
            )
        )
        version = result.scalar_one()
        
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/{version.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == version.id
        assert data["version_number"] == 1
        assert data["title"] == "Test Article"
        assert data["content"] == "Initial content"
        assert data["change_summary"] == "Initial creation"
        assert data["change_type"] == "create"
    
    async def test_get_version_not_found(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict
    ):
        """Test getting non-existent version."""
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/non-existent-version",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestRestoreVersion:
    """Tests for restoring to a previous version."""
    
    async def test_restore_version_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test restoring a knowledge item to a previous version."""
        # Get version 1
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 1
            )
        )
        version = result.scalar_one()
        
        response = await client.post(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/{version.id}/restore",
            json={"create_backup": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that content was restored
        assert data["title"] == "Test Article"
        assert data["content"] == "Initial content"
        
        # Verify new versions were created (backup + restore)
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id
            )
        )
        versions = result.scalars().all()
        assert len(versions) >= 5  # Original 3 + backup + restore
    
    async def test_restore_version_without_backup(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test restoring without creating backup."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 2
            )
        )
        version = result.scalar_one()
        
        response = await client.post(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/{version.id}/restore",
            json={"create_backup": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestCompareVersions:
    """Tests for comparing two versions."""
    
    async def test_compare_versions_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test comparing two versions."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        # Get version 1 and version 2
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id
            ).order_by(KnowledgeVersion.version_number)
        )
        versions = result.scalars().all()
        version1 = versions[0]
        version2 = versions[1]
        
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/compare",
            params={
                "version_id_1": version1.id,
                "version_id_2": version2.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "version_1" in data
        assert "version_2" in data
        assert "title_diff" in data
        assert "content_diff" in data
        assert "summary" in data
        
        # Check versions
        assert data["version_1"]["version_number"] == 1
        assert data["version_2"]["version_number"] == 2
        
        # Check summary statistics
        summary = data["summary"]
        assert "title_changes" in summary
        assert "content_changes" in summary
        assert "insertions" in summary
        assert "deletions" in summary
        assert "replacements" in summary
        
        # Should have changes since content is different
        assert summary["content_changes"] > 0
    
    async def test_compare_same_version(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test comparing a version with itself."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 1
            )
        )
        version = result.scalar_one()
        
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/compare",
            params={
                "version_id_1": version.id,
                "version_id_2": version.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have no changes
        summary = data["summary"]
        assert summary["content_changes"] == 0
        assert summary["insertions"] == 0
        assert summary["deletions"] == 0


class TestDeleteVersion:
    """Tests for deleting a version."""
    
    async def test_delete_old_version_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test deleting an old version."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        # Get version 1 (not the most recent)
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 1
            )
        )
        version = result.scalar_one()
        
        response = await client.delete(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/{version.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify version was deleted
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.id == version.id
            )
        )
        deleted_version = result.scalar_one_or_none()
        assert deleted_version is None
    
    async def test_delete_most_recent_version_fails(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test that deleting the most recent version fails."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        # Get the most recent version (version 3)
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id,
                KnowledgeVersion.version_number == 3
            )
        )
        version = result.scalar_one()
        
        response = await client.delete(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/{version.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "most recent version" in response.json()["detail"].lower()


class TestCleanupVersions:
    """Tests for cleaning up old versions."""
    
    async def test_cleanup_versions_success(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test cleaning up old versions."""
        # Create more versions to test cleanup
        from app.models.knowledge import KnowledgeVersion
        import uuid
        
        for i in range(4, 15):  # Add versions 4-14
            version = KnowledgeVersion(
                id=str(uuid.uuid4()),
                knowledge_item_id=test_knowledge_item.id,
                version_number=i,
                title=f"Version {i}",
                content=f"Content {i}",
                content_type="markdown",
                change_summary=f"Update {i}",
                change_type="edit",
                created_by=test_knowledge_item.author_id,
                created_at=datetime.utcnow()
            )
            db_session.add(version)
        
        await db_session.commit()
        
        # Now we have 14 versions total
        response = await client.post(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/cleanup",
            json={"keep_count": 5, "compress_old": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_versions"] == 14
        assert data["deleted_count"] == 9  # 14 - 5 = 9
        assert data["kept_count"] == 5
        
        # Verify only 5 versions remain
        from sqlalchemy import select, func
        result = await db_session.execute(
            select(func.count()).select_from(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id
            )
        )
        count = result.scalar()
        assert count == 5
    
    async def test_cleanup_versions_within_limit(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict
    ):
        """Test cleanup when versions are within keep limit."""
        response = await client.post(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/cleanup",
            json={"keep_count": 10, "compress_old": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not delete any versions since we have only 3
        assert data["deleted_count"] == 0
        assert "within keep limit" in data["message"].lower()


class TestVersionControlEdgeCases:
    """Tests for edge cases and error handling."""
    
    async def test_version_control_permission_denied(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        db_session: AsyncSession
    ):
        """Test that other users cannot access version control."""
        # Create another user
        other_user = User(
            id="other-user-version",
            username="otheruser",
            email="other@test.com",
            hashed_password="hashed_password",
            is_active=True
        )
        db_session.add(other_user)
        await db_session.commit()
        
        # Create token for other user
        token = create_access_token(other_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get versions
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions",
            headers=headers
        )
        
        assert response.status_code == 403
    
    async def test_version_diff_algorithm(
        self,
        client: AsyncClient,
        test_knowledge_item: KnowledgeItem,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test that diff algorithm correctly identifies changes."""
        from sqlalchemy import select
        from app.models.knowledge import KnowledgeVersion
        
        # Get versions with different content
        result = await db_session.execute(
            select(KnowledgeVersion).where(
                KnowledgeVersion.knowledge_item_id == test_knowledge_item.id
            ).order_by(KnowledgeVersion.version_number)
        )
        versions = result.scalars().all()
        
        response = await client.get(
            f"/api/v1/knowledge/{test_knowledge_item.id}/versions/compare",
            params={
                "version_id_1": versions[0].id,
                "version_id_2": versions[2].id
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that diff operations are present
        content_diff = data["content_diff"]
        assert len(content_diff) > 0
        
        # Check diff structure
        for diff in content_diff:
            assert "operation" in diff
            assert diff["operation"] in ["equal", "insert", "delete", "replace"]
            assert "old_start" in diff
            assert "old_end" in diff
            assert "new_start" in diff
            assert "new_end" in diff
