"""
Tag Service

Business logic for tag management.
"""

import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.core.exceptions import NotFoundError, PermissionError, ValidationError


class TagService:
    """Service class for tag operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tag(self, user_id: str, data: TagCreate) -> Tag:
        """Create a new tag."""
        
        # Check if tag with same name already exists for this user
        existing = await self.get_tag_by_name(user_id, data.name)
        if existing:
            raise ValidationError(f"Tag '{data.name}' already exists")
        
        tag = Tag(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            color=data.color or "#95a5a6",
            user_id=user_id,
            is_system=False,
            created_at=datetime.utcnow()
        )
        
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        
        logger.info(f"Tag created: {tag.id} ({tag.name}) by user {user_id}")
        return tag
    
    async def get_tag(self, tag_id: str, user_id: str) -> Tag:
        """Get a tag by ID."""
        
        result = await self.db.execute(
            select(Tag).where(
                Tag.id == tag_id,
                or_(Tag.user_id == user_id, Tag.is_system == True),
                Tag.is_active == True
            )
        )
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise NotFoundError("Tag not found")
        
        return tag
    
    async def get_tag_by_name(self, user_id: str, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        
        result = await self.db.execute(
            select(Tag).where(
                Tag.name == name,
                Tag.user_id == user_id,
                Tag.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def list_tags(
        self,
        user_id: str,
        search: Optional[str] = None,
        include_system: bool = True
    ) -> List[Tag]:
        """List all tags for a user."""
        
        query = select(Tag).where(Tag.is_active == True)
        
        if include_system:
            query = query.where(
                or_(Tag.user_id == user_id, Tag.is_system == True)
            )
        else:
            query = query.where(Tag.user_id == user_id)
        
        if search:
            query = query.where(Tag.name.ilike(f"%{search}%"))
        
        query = query.order_by(Tag.usage_count.desc(), Tag.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_tag(
        self,
        tag_id: str,
        user_id: str,
        data: TagUpdate
    ) -> Tag:
        """Update a tag."""
        
        tag = await self.get_tag(tag_id, user_id)
        
        # Check ownership
        if tag.user_id != user_id:
            raise PermissionError("You can only update your own tags")
        
        if tag.is_system:
            raise PermissionError("Cannot update system tags")
        
        if data.name is not None:
            # Check if new name conflicts
            existing = await self.get_tag_by_name(user_id, data.name)
            if existing and existing.id != tag_id:
                raise ValidationError(f"Tag '{data.name}' already exists")
            tag.name = data.name
        
        if data.description is not None:
            tag.description = data.description
        
        if data.color is not None:
            tag.color = data.color
        
        tag.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(tag)
        
        logger.info(f"Tag updated: {tag.id} by user {user_id}")
        return tag
    
    async def delete_tag(self, tag_id: str, user_id: str) -> bool:
        """Delete a tag."""
        
        tag = await self.get_tag(tag_id, user_id)
        
        # Check ownership
        if tag.user_id != user_id:
            raise PermissionError("You can only delete your own tags")
        
        if tag.is_system:
            raise PermissionError("Cannot delete system tags")
        
        # Soft delete
        tag.is_active = False
        tag.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Tag deleted: {tag.id} by user {user_id}")
        return True
    
    async def merge_tags(
        self,
        source_tag_id: str,
        target_tag_id: str,
        user_id: str
    ) -> Tag:
        """Merge source tag into target tag."""
        
        source_tag = await self.get_tag(source_tag_id, user_id)
        target_tag = await self.get_tag(target_tag_id, user_id)
        
        # Check ownership
        if source_tag.user_id != user_id or target_tag.user_id != user_id:
            raise PermissionError("You can only merge your own tags")
        
        if source_tag.is_system or target_tag.is_system:
            raise PermissionError("Cannot merge system tags")
        
        # Merge
        source_tag.merge_into(target_tag)
        
        await self.db.commit()
        await self.db.refresh(target_tag)
        
        logger.info(f"Tags merged: {source_tag_id} -> {target_tag_id} by user {user_id}")
        return target_tag
    
    async def get_popular_tags(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Tag]:
        """Get most popular tags by usage count."""
        
        query = select(Tag).where(
            or_(Tag.user_id == user_id, Tag.is_system == True),
            Tag.is_active == True,
            Tag.usage_count > 0
        ).order_by(Tag.usage_count.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def autocomplete_tags(
        self,
        user_id: str,
        prefix: str,
        limit: int = 10
    ) -> List[Tag]:
        """Autocomplete tag names."""
        
        query = select(Tag).where(
            or_(Tag.user_id == user_id, Tag.is_system == True),
            Tag.is_active == True,
            Tag.name.ilike(f"{prefix}%")
        ).order_by(Tag.usage_count.desc(), Tag.name).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
