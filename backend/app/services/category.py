"""
Category Service

Business logic for category management with hierarchical operations.
"""

import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import NotFoundError, PermissionError, ValidationError


class CategoryService:
    """Service class for category operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_category(self, user_id: str, data: CategoryCreate) -> Category:
        """Create a new category."""
        
        # Check if category with same name already exists for this user at same level
        existing = await self._get_category_by_name(user_id, data.name, data.parent_id)
        if existing:
            raise ValidationError(f"Category '{data.name}' already exists at this level")
        
        # Validate parent exists if provided
        if data.parent_id:
            parent = await self.get_category(data.parent_id, user_id)
            if not parent:
                raise NotFoundError("Parent category not found")
        
        category = Category(
            id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
            user_id=user_id,
            color=data.color or "#3498db",
            icon=data.icon,
            sort_order=data.sort_order or 0,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        logger.info(f"Category created: {category.id} ({category.name}) by user {user_id}")
        return category
    
    async def get_category(self, category_id: str, user_id: str) -> Category:
        """Get a category by ID."""
        
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.parent), selectinload(Category.children))
            .where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_active == True
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            raise NotFoundError("Category not found")
        
        return category
    
    async def _get_category_by_name(
        self,
        user_id: str,
        name: str,
        parent_id: Optional[str] = None
    ) -> Optional[Category]:
        """Get a category by name at a specific level."""
        
        query = select(Category).where(
            Category.name == name,
            Category.user_id == user_id,
            Category.is_active == True
        )
        
        if parent_id:
            query = query.where(Category.parent_id == parent_id)
        else:
            query = query.where(Category.parent_id.is_(None))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_categories(
        self,
        user_id: str,
        parent_id: Optional[str] = None,
        include_children: bool = False
    ) -> List[Category]:
        """List categories for a user, optionally filtered by parent."""
        
        query = select(Category).where(
            Category.user_id == user_id,
            Category.is_active == True
        )
        
        if parent_id:
            query = query.where(Category.parent_id == parent_id)
        elif not include_children:
            # Only root categories
            query = query.where(Category.parent_id.is_(None))
        
        query = query.order_by(Category.sort_order, Category.name)
        
        if include_children:
            query = query.options(selectinload(Category.children))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_category_tree(self, user_id: str) -> List[Category]:
        """Get full category tree with all descendants loaded."""
        
        # Get all categories for user
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(
                Category.user_id == user_id,
                Category.is_active == True
            )
            .order_by(Category.sort_order, Category.name)
        )
        all_categories = result.scalars().all()
        
        # Return only root categories (tree structure via relationships)
        return [cat for cat in all_categories if cat.parent_id is None]
    
    async def update_category(
        self,
        category_id: str,
        user_id: str,
        data: CategoryUpdate
    ) -> Category:
        """Update a category."""
        
        category = await self.get_category(category_id, user_id)
        
        # Check ownership
        if category.user_id != user_id:
            raise PermissionError("You can only update your own categories")
        
        if data.name is not None:
            # Check if new name conflicts at same level
            existing = await self._get_category_by_name(user_id, data.name, category.parent_id)
            if existing and existing.id != category_id:
                raise ValidationError(f"Category '{data.name}' already exists at this level")
            category.name = data.name
        
        if data.description is not None:
            category.description = data.description
        
        if data.color is not None:
            category.color = data.color
        
        if data.icon is not None:
            category.icon = data.icon
        
        if data.sort_order is not None:
            category.sort_order = data.sort_order
        
        if data.parent_id is not None:
            # Validate new parent
            if data.parent_id != category.parent_id:
                await self._validate_parent_change(category, data.parent_id, user_id)
                category.parent_id = data.parent_id
        
        category.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(category)
        
        logger.info(f"Category updated: {category.id} by user {user_id}")
        return category
    
    async def _validate_parent_change(
        self,
        category: Category,
        new_parent_id: str,
        user_id: str
    ) -> None:
        """Validate that parent change doesn't create circular reference."""
        
        if new_parent_id == category.id:
            raise ValidationError("Category cannot be its own parent")
        
        # Get new parent
        new_parent = await self.get_category(new_parent_id, user_id)
        
        # Check if new parent is a descendant of this category
        if new_parent.is_descendant_of(category):
            raise ValidationError("Cannot move category to its own descendant")
    
    async def delete_category(
        self,
        category_id: str,
        user_id: str,
        delete_children: bool = False
    ) -> bool:
        """Delete a category."""
        
        category = await self.get_category(category_id, user_id)
        
        # Check ownership
        if category.user_id != user_id:
            raise PermissionError("You can only delete your own categories")
        
        # Check if category has children
        if category.children and not delete_children:
            raise ValidationError(
                "Category has child categories. Set delete_children=True to delete them too, "
                "or move them to another parent first."
            )
        
        # Soft delete
        category.is_active = False
        category.updated_at = datetime.utcnow()
        
        # Delete children if requested
        if delete_children:
            for child in category.get_descendants():
                child.is_active = False
                child.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Category deleted: {category.id} by user {user_id}")
        return True
    
    async def move_category(
        self,
        category_id: str,
        new_parent_id: Optional[str],
        user_id: str
    ) -> Category:
        """Move a category to a new parent."""
        
        category = await self.get_category(category_id, user_id)
        
        # Check ownership
        if category.user_id != user_id:
            raise PermissionError("You can only move your own categories")
        
        if new_parent_id:
            await self._validate_parent_change(category, new_parent_id, user_id)
        
        category.parent_id = new_parent_id
        category.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(category)
        
        logger.info(f"Category moved: {category.id} to parent {new_parent_id} by user {user_id}")
        return category
    
    async def merge_categories(
        self,
        source_category_id: str,
        target_category_id: str,
        user_id: str
    ) -> Category:
        """Merge source category into target category."""
        
        source = await self.get_category(source_category_id, user_id)
        target = await self.get_category(target_category_id, user_id)
        
        # Check ownership
        if source.user_id != user_id or target.user_id != user_id:
            raise PermissionError("You can only merge your own categories")
        
        # Validate merge won't create circular reference
        if target.is_descendant_of(source):
            raise ValidationError("Cannot merge category into its own descendant")
        
        # Move all knowledge items from source to target
        for item in source.knowledge_items:
            item.category_id = target.id
        
        # Move all children from source to target
        for child in source.children:
            child.parent_id = target.id
        
        # Soft delete source
        source.is_active = False
        source.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(target)
        
        logger.info(f"Categories merged: {source_category_id} -> {target_category_id} by user {user_id}")
        return target
    
    async def get_category_stats(self, category_id: str, user_id: str) -> dict:
        """Get statistics for a category."""
        
        category = await self.get_category(category_id, user_id)
        
        # Count knowledge items in this category
        from app.models.knowledge import KnowledgeItem
        result = await self.db.execute(
            select(KnowledgeItem).where(
                KnowledgeItem.category_id == category_id,
                KnowledgeItem.is_deleted == False
            )
        )
        items = result.scalars().all()
        
        # Count descendants
        descendants = category.get_descendants()
        
        return {
            "category_id": category.id,
            "name": category.name,
            "depth": category.depth,
            "item_count": len(items),
            "child_count": len(category.children),
            "descendant_count": len(descendants),
            "full_path": category.full_path
        }
