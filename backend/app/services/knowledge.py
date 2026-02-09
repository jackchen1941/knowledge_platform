"""
Knowledge Service

Business logic for knowledge item management.
"""

import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from math import ceil

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.knowledge import KnowledgeItem, KnowledgeVersion
from app.models.tag import Tag
from app.models.category import Category
from app.schemas.knowledge import (
    KnowledgeCreate, KnowledgeUpdate, KnowledgeDraft, 
    KnowledgeFilter, KnowledgeListResponse,
    VersionListResponse, VersionListItem, VersionCompareResponse,
    VersionDiff, VersionCleanupRequest
)
from app.core.exceptions import NotFoundError, PermissionError, ValidationError


class KnowledgeService:
    """Service class for knowledge item operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_knowledge_item(
        self, 
        user_id: str, 
        data: KnowledgeCreate
    ) -> KnowledgeItem:
        """Create a new knowledge item with initial version."""
        
        # Calculate word count and reading time
        word_count = self._calculate_word_count(data.content)
        reading_time = self._calculate_reading_time(word_count)
        
        # Create knowledge item
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            title=data.title,
            content=data.content,
            content_type=data.content_type,
            summary=data.summary,
            author_id=user_id,
            category_id=data.category_id,
            source_platform=data.source_platform,
            source_url=data.source_url,
            source_id=data.source_id,
            is_published=data.is_published,
            visibility=data.visibility,
            meta_data=data.meta_data or {},
            word_count=word_count,
            reading_time=reading_time,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        if data.is_published:
            item.published_at = datetime.utcnow()
        
        self.db.add(item)
        
        # Handle tags
        if data.tag_ids:
            await self._attach_tags(item, data.tag_ids, user_id)
        
        # Create initial version
        version = item.create_version(
            user_id=user_id,
            change_summary="Initial creation",
            change_type="create"
        )
        self.db.add(version)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Knowledge item created: {item.id} by user {user_id}")
        return item
    
    async def get_knowledge_item(
        self, 
        item_id: str, 
        user_id: str,
        include_deleted: bool = False
    ) -> KnowledgeItem:
        """Get a knowledge item by ID with permission check."""
        
        query = select(KnowledgeItem).where(KnowledgeItem.id == item_id)
        
        if not include_deleted:
            query = query.where(KnowledgeItem.is_deleted == False)
        
        query = query.options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category),
            selectinload(KnowledgeItem.attachments)
        )
        
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundError("Knowledge item not found")
        
        # Check permissions
        if item.author_id != user_id and item.visibility == "private":
            raise PermissionError("You don't have permission to access this item")
        
        # Increment view count
        item.view_count += 1
        await self.db.commit()
        
        return item
    
    async def list_knowledge_items(
        self,
        user_id: str,
        filters: KnowledgeFilter
    ) -> KnowledgeListResponse:
        """List knowledge items with filtering and pagination."""
        
        # Build base query
        query = select(KnowledgeItem).where(
            or_(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.visibility.in_(["shared", "public"])
            )
        )
        
        # Apply filters
        if filters.is_deleted is not None:
            query = query.where(KnowledgeItem.is_deleted == filters.is_deleted)
        else:
            query = query.where(KnowledgeItem.is_deleted == False)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    KnowledgeItem.title.ilike(search_term),
                    KnowledgeItem.content.ilike(search_term),
                    KnowledgeItem.summary.ilike(search_term)
                )
            )
        
        if filters.category_id:
            query = query.where(KnowledgeItem.category_id == filters.category_id)
        
        if filters.visibility:
            query = query.where(KnowledgeItem.visibility == filters.visibility)
        
        if filters.is_published is not None:
            query = query.where(KnowledgeItem.is_published == filters.is_published)
        
        if filters.source_platform:
            query = query.where(KnowledgeItem.source_platform == filters.source_platform)
        
        if filters.created_after:
            query = query.where(KnowledgeItem.created_at >= filters.created_after)
        
        if filters.created_before:
            query = query.where(KnowledgeItem.created_at <= filters.created_before)
        
        if filters.updated_after:
            query = query.where(KnowledgeItem.updated_at >= filters.updated_after)
        
        if filters.updated_before:
            query = query.where(KnowledgeItem.updated_at <= filters.updated_before)
        
        # Handle tag filtering
        if filters.tag_ids:
            # Join with tags and filter
            from app.models.tag import knowledge_item_tags
            query = query.join(knowledge_item_tags).where(
                knowledge_item_tags.c.tag_id.in_(filters.tag_ids)
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(KnowledgeItem, filters.sort_by)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        
        # Load relationships
        query = query.options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category)
        )
        
        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Calculate total pages
        total_pages = ceil(total / filters.page_size) if total > 0 else 0
        
        return KnowledgeListResponse(
            items=items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages
        )
    
    async def update_knowledge_item(
        self,
        item_id: str,
        user_id: str,
        data: KnowledgeUpdate
    ) -> KnowledgeItem:
        """Update a knowledge item and create a new version."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only update your own knowledge items")
        
        # Create version before updating
        version = item.create_version(
            user_id=user_id,
            change_summary=data.change_summary or "Content updated",
            change_type="edit"
        )
        self.db.add(version)
        
        # Update fields
        if data.title is not None:
            item.title = data.title
        
        if data.content is not None:
            item.content = data.content
            # Recalculate word count and reading time
            item.word_count = self._calculate_word_count(data.content)
            item.reading_time = self._calculate_reading_time(item.word_count)
        
        if data.content_type is not None:
            item.content_type = data.content_type
        
        if data.summary is not None:
            item.summary = data.summary
        
        if data.category_id is not None:
            item.category_id = data.category_id
        
        if data.visibility is not None:
            item.visibility = data.visibility
        
        if data.source_platform is not None:
            item.source_platform = data.source_platform
        
        if data.source_url is not None:
            item.source_url = data.source_url
        
        if data.meta_data is not None:
            item.meta_data = data.meta_data
        
        # Handle tags
        if data.tag_ids is not None:
            await self._update_tags(item, data.tag_ids, user_id)
        
        item.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Knowledge item updated: {item.id} by user {user_id}")
        return item
    
    async def save_draft(
        self,
        item_id: str,
        user_id: str,
        data: KnowledgeDraft
    ) -> KnowledgeItem:
        """Save draft changes without creating a version."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only update your own knowledge items")
        
        # Update fields (draft mode - no version created)
        if data.title is not None:
            item.title = data.title
        
        if data.content is not None:
            item.content = data.content
            item.word_count = self._calculate_word_count(data.content)
            item.reading_time = self._calculate_reading_time(item.word_count)
        
        if data.content_type is not None:
            item.content_type = data.content_type
        
        if data.summary is not None:
            item.summary = data.summary
        
        if data.category_id is not None:
            item.category_id = data.category_id
        
        if data.meta_data is not None:
            item.meta_data = data.meta_data
        
        if data.tag_ids is not None:
            await self._update_tags(item, data.tag_ids, user_id)
        
        # Mark as unpublished (draft)
        item.is_published = False
        item.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Draft saved: {item.id} by user {user_id}")
        return item
    
    async def publish_knowledge_item(
        self,
        item_id: str,
        user_id: str
    ) -> KnowledgeItem:
        """Publish a knowledge item."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only publish your own knowledge items")
        
        if not item.is_published:
            # Create version for publishing
            version = item.create_version(
                user_id=user_id,
                change_summary="Published",
                change_type="publish"
            )
            self.db.add(version)
            
            item.is_published = True
            item.published_at = datetime.utcnow()
            item.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(item)
            
            logger.info(f"Knowledge item published: {item.id} by user {user_id}")
        
        return item
    
    async def delete_knowledge_item(
        self,
        item_id: str,
        user_id: str
    ) -> KnowledgeItem:
        """Soft delete a knowledge item."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only delete your own knowledge items")
        
        # Soft delete
        item.soft_delete()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Knowledge item deleted: {item.id} by user {user_id}")
        return item
    
    async def restore_knowledge_item(
        self,
        item_id: str,
        user_id: str
    ) -> KnowledgeItem:
        """Restore a soft-deleted knowledge item."""
        
        # Get item including deleted ones
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=True)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only restore your own knowledge items")
        
        # Check if item is deleted
        if not item.is_deleted:
            raise ValidationError("Item is not deleted")
        
        # Check if item is still recoverable
        if not item.is_recoverable:
            raise ValidationError("Item cannot be recovered (30-day limit exceeded)")
        
        # Restore
        item.restore()
        
        # Create version for restore
        version = item.create_version(
            user_id=user_id,
            change_summary="Restored from recycle bin",
            change_type="restore"
        )
        self.db.add(version)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Knowledge item restored: {item.id} by user {user_id}")
        return item
    
    async def get_deleted_items(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> KnowledgeListResponse:
        """Get deleted items (recycle bin)."""
        
        filters = KnowledgeFilter(
            is_deleted=True,
            page=page,
            page_size=page_size,
            sort_by="deleted_at",
            sort_order="desc"
        )
        
        # Modify query to only show user's own deleted items
        query = select(KnowledgeItem).where(
            and_(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == True
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Load relationships
        query = query.options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category)
        )
        
        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        # Calculate total pages
        total_pages = ceil(total / page_size) if total > 0 else 0
        
        return KnowledgeListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def search_knowledge_items(
        self,
        user_id: str,
        search_query: str,
        page: int = 1,
        page_size: int = 20
    ) -> KnowledgeListResponse:
        """Search knowledge items by title, content, or summary."""
        
        filters = KnowledgeFilter(
            search=search_query,
            page=page,
            page_size=page_size,
            sort_by="updated_at",
            sort_order="desc"
        )
        
        return await self.list_knowledge_items(user_id, filters)
    
    # Helper methods
    
    def _calculate_word_count(self, content: str) -> int:
        """Calculate word count from content."""
        # Remove markdown/html tags for more accurate count
        text = re.sub(r'<[^>]+>', '', content)
        text = re.sub(r'[#*`\[\]()]', '', text)
        
        # Count words (split by whitespace)
        words = text.split()
        return len(words)
    
    def _calculate_reading_time(self, word_count: int) -> int:
        """Calculate estimated reading time in minutes (assuming 200 words/min)."""
        return max(1, round(word_count / 200))
    
    async def _attach_tags(
        self,
        item: KnowledgeItem,
        tag_ids: List[str],
        user_id: str
    ) -> None:
        """Attach tags to a knowledge item."""
        
        # Get tags
        result = await self.db.execute(
            select(Tag).where(
                and_(
                    Tag.id.in_(tag_ids),
                    or_(
                        Tag.user_id == user_id,
                        Tag.is_system == True
                    )
                )
            )
        )
        tags = result.scalars().all()
        
        # Attach tags and increment usage
        for tag in tags:
            item.tags.append(tag)
            tag.increment_usage()
    
    async def _update_tags(
        self,
        item: KnowledgeItem,
        tag_ids: List[str],
        user_id: str
    ) -> None:
        """Update tags for a knowledge item."""
        
        # Get current tags
        current_tag_ids = {tag.id for tag in item.tags}
        new_tag_ids = set(tag_ids)
        
        # Tags to remove
        tags_to_remove = current_tag_ids - new_tag_ids
        for tag in item.tags[:]:
            if tag.id in tags_to_remove:
                item.tags.remove(tag)
                tag.decrement_usage()
        
        # Tags to add
        tags_to_add = new_tag_ids - current_tag_ids
        if tags_to_add:
            result = await self.db.execute(
                select(Tag).where(
                    and_(
                        Tag.id.in_(tags_to_add),
                        or_(
                            Tag.user_id == user_id,
                            Tag.is_system == True
                        )
                    )
                )
            )
            new_tags = result.scalars().all()
            
            for tag in new_tags:
                item.tags.append(tag)
                tag.increment_usage()
    
    # Version control methods
    
    async def get_versions(
        self,
        item_id: str,
        user_id: str
    ) -> VersionListResponse:
        """Get all versions for a knowledge item."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Get all versions ordered by version number descending
        query = select(KnowledgeVersion).where(
            KnowledgeVersion.knowledge_item_id == item_id
        ).order_by(KnowledgeVersion.version_number.desc())
        
        result = await self.db.execute(query)
        versions = result.scalars().all()
        
        # Convert to list items with content preview
        version_items = []
        for version in versions:
            content_preview = version.content[:200] + "..." if len(version.content) > 200 else version.content
            version_items.append(VersionListItem(
                id=version.id,
                version_number=version.version_number,
                title=version.title,
                change_summary=version.change_summary,
                change_type=version.change_type,
                created_by=version.created_by,
                created_at=version.created_at,
                content_preview=content_preview
            ))
        
        return VersionListResponse(
            versions=version_items,
            total=len(version_items),
            knowledge_item_id=item_id
        )
    
    async def get_version(
        self,
        item_id: str,
        version_id: str,
        user_id: str
    ) -> KnowledgeVersion:
        """Get a specific version by ID."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Get version
        query = select(KnowledgeVersion).where(
            and_(
                KnowledgeVersion.id == version_id,
                KnowledgeVersion.knowledge_item_id == item_id
            )
        )
        
        result = await self.db.execute(query)
        version = result.scalar_one_or_none()
        
        if not version:
            raise NotFoundError("Version not found")
        
        return version
    
    async def restore_version(
        self,
        item_id: str,
        version_id: str,
        user_id: str,
        create_backup: bool = True
    ) -> KnowledgeItem:
        """Restore a knowledge item to a specific version."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only restore your own knowledge items")
        
        # Get version
        version = await self.get_version(item_id, version_id, user_id)
        
        # Restore using the model method
        version.restore_to_item(user_id)
        
        await self.db.commit()
        await self.db.refresh(item)
        
        logger.info(f"Knowledge item {item_id} restored to version {version.version_number} by user {user_id}")
        return item
    
    async def compare_versions(
        self,
        item_id: str,
        version_id_1: str,
        version_id_2: str,
        user_id: str
    ) -> VersionCompareResponse:
        """Compare two versions and return differences."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Get both versions
        version_1 = await self.get_version(item_id, version_id_1, user_id)
        version_2 = await self.get_version(item_id, version_id_2, user_id)
        
        # Calculate diffs
        title_diff = self._calculate_diff(version_1.title, version_2.title)
        content_diff = self._calculate_diff(version_1.content, version_2.content)
        
        # Calculate summary statistics
        summary = {
            "title_changes": len([d for d in title_diff if d.operation != "equal"]),
            "content_changes": len([d for d in content_diff if d.operation != "equal"]),
            "insertions": len([d for d in content_diff if d.operation == "insert"]),
            "deletions": len([d for d in content_diff if d.operation == "delete"]),
            "replacements": len([d for d in content_diff if d.operation == "replace"])
        }
        
        return VersionCompareResponse(
            version_1=version_1,
            version_2=version_2,
            title_diff=title_diff,
            content_diff=content_diff,
            summary=summary
        )
    
    async def delete_version(
        self,
        item_id: str,
        version_id: str,
        user_id: str
    ) -> bool:
        """Delete a specific version (for cleanup)."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only delete versions of your own knowledge items")
        
        # Get version
        version = await self.get_version(item_id, version_id, user_id)
        
        # Don't allow deleting the most recent version
        query = select(func.max(KnowledgeVersion.version_number)).where(
            KnowledgeVersion.knowledge_item_id == item_id
        )
        result = await self.db.execute(query)
        max_version = result.scalar()
        
        if version.version_number == max_version:
            raise ValidationError("Cannot delete the most recent version")
        
        # Delete the version
        await self.db.delete(version)
        await self.db.commit()
        
        logger.info(f"Version {version_id} deleted from item {item_id} by user {user_id}")
        return True
    
    async def cleanup_versions(
        self,
        item_id: str,
        user_id: str,
        keep_count: int = 10
    ) -> Dict[str, Any]:
        """Clean up old versions, keeping only the most recent ones."""
        
        # Get item with permission check
        item = await self.get_knowledge_item(item_id, user_id, include_deleted=False)
        
        # Check ownership
        if item.author_id != user_id:
            raise PermissionError("You can only cleanup versions of your own knowledge items")
        
        # Get all versions ordered by version number descending
        query = select(KnowledgeVersion).where(
            KnowledgeVersion.knowledge_item_id == item_id
        ).order_by(KnowledgeVersion.version_number.desc())
        
        result = await self.db.execute(query)
        versions = result.scalars().all()
        
        total_versions = len(versions)
        
        # Keep the most recent versions
        if total_versions <= keep_count:
            return {
                "total_versions": total_versions,
                "deleted_count": 0,
                "kept_count": total_versions,
                "message": "No versions deleted (within keep limit)"
            }
        
        # Delete old versions
        versions_to_delete = versions[keep_count:]
        deleted_count = 0
        
        for version in versions_to_delete:
            await self.db.delete(version)
            deleted_count += 1
        
        await self.db.commit()
        
        logger.info(f"Cleaned up {deleted_count} versions from item {item_id} by user {user_id}")
        
        return {
            "total_versions": total_versions,
            "deleted_count": deleted_count,
            "kept_count": keep_count,
            "message": f"Successfully deleted {deleted_count} old versions"
        }
    
    def _calculate_diff(self, text1: str, text2: str) -> List[VersionDiff]:
        """Calculate differences between two texts using a simple diff algorithm."""
        import difflib
        
        # Split texts into lines for better diff
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # Use difflib to get differences
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        diffs = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                diffs.append(VersionDiff(
                    operation='equal',
                    old_start=i1,
                    old_end=i2,
                    new_start=j1,
                    new_end=j2,
                    old_text=''.join(lines1[i1:i2]),
                    new_text=''.join(lines2[j1:j2])
                ))
            elif tag == 'insert':
                diffs.append(VersionDiff(
                    operation='insert',
                    old_start=i1,
                    old_end=i2,
                    new_start=j1,
                    new_end=j2,
                    old_text=None,
                    new_text=''.join(lines2[j1:j2])
                ))
            elif tag == 'delete':
                diffs.append(VersionDiff(
                    operation='delete',
                    old_start=i1,
                    old_end=i2,
                    new_start=j1,
                    new_end=j2,
                    old_text=''.join(lines1[i1:i2]),
                    new_text=None
                ))
            elif tag == 'replace':
                diffs.append(VersionDiff(
                    operation='replace',
                    old_start=i1,
                    old_end=i2,
                    new_start=j1,
                    new_end=j2,
                    old_text=''.join(lines1[i1:i2]),
                    new_text=''.join(lines2[j1:j2])
                ))
        
        return diffs
