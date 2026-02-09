"""
Search Service

Business logic for search and filtering operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.knowledge import KnowledgeItem
from app.models.tag import Tag
from app.models.category import Category
from app.schemas.search import SearchQuery, SearchResult, SearchSuggestion


class SearchService:
    """Service class for search operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search(
        self,
        user_id: str,
        query: SearchQuery
    ) -> tuple[List[KnowledgeItem], int]:
        """
        Perform full-text search on knowledge items.
        Returns (items, total_count).
        """
        
        # Build base query
        stmt = select(KnowledgeItem).where(
            KnowledgeItem.author_id == user_id,
            KnowledgeItem.is_deleted == False
        )
        
        # Add eager loading for relationships
        stmt = stmt.options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category),
            selectinload(KnowledgeItem.attachments)
        )
        
        # Full-text search on title and content
        if query.q:
            search_term = f"%{query.q}%"
            stmt = stmt.where(
                or_(
                    KnowledgeItem.title.ilike(search_term),
                    KnowledgeItem.content.ilike(search_term),
                    KnowledgeItem.summary.ilike(search_term)
                )
            )
        
        # Filter by category
        if query.category_id:
            stmt = stmt.where(KnowledgeItem.category_id == query.category_id)
        
        # Filter by tags
        if query.tag_ids:
            # Join with tags and filter
            from app.models.tag import knowledge_item_tags
            stmt = stmt.join(knowledge_item_tags).where(
                knowledge_item_tags.c.tag_id.in_(query.tag_ids)
            )
        
        # Filter by visibility
        if query.visibility:
            stmt = stmt.where(KnowledgeItem.visibility == query.visibility)
        
        # Filter by published status
        if query.is_published is not None:
            stmt = stmt.where(KnowledgeItem.is_published == query.is_published)
        
        # Filter by source platform
        if query.source_platform:
            stmt = stmt.where(KnowledgeItem.source_platform == query.source_platform)
        
        # Filter by date range
        if query.created_after:
            stmt = stmt.where(KnowledgeItem.created_at >= query.created_after)
        if query.created_before:
            stmt = stmt.where(KnowledgeItem.created_at <= query.created_before)
        if query.updated_after:
            stmt = stmt.where(KnowledgeItem.updated_at >= query.updated_after)
        if query.updated_before:
            stmt = stmt.where(KnowledgeItem.updated_at <= query.updated_before)
        
        # Filter by content type
        if query.content_type:
            stmt = stmt.where(KnowledgeItem.content_type == query.content_type)
        
        # Filter by word count range
        if query.min_word_count:
            stmt = stmt.where(KnowledgeItem.word_count >= query.min_word_count)
        if query.max_word_count:
            stmt = stmt.where(KnowledgeItem.word_count <= query.max_word_count)
        
        # Get total count before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(KnowledgeItem, query.sort_by, KnowledgeItem.updated_at)
        if query.sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (query.page - 1) * query.page_size
        stmt = stmt.offset(offset).limit(query.page_size)
        
        # Execute query
        result = await self.db.execute(stmt)
        items = result.scalars().unique().all()
        
        logger.info(f"Search performed by user {user_id}: query='{query.q}', results={len(items)}/{total}")
        return items, total
    
    async def get_suggestions(
        self,
        user_id: str,
        prefix: str,
        limit: int = 10
    ) -> List[SearchSuggestion]:
        """Get search suggestions based on prefix."""
        
        suggestions = []
        
        # Search in knowledge item titles
        stmt = select(KnowledgeItem.title, KnowledgeItem.id).where(
            KnowledgeItem.author_id == user_id,
            KnowledgeItem.is_deleted == False,
            KnowledgeItem.title.ilike(f"{prefix}%")
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        items = result.all()
        
        for title, item_id in items:
            suggestions.append(SearchSuggestion(
                text=title,
                type="knowledge_item",
                id=item_id
            ))
        
        # Search in tags
        if len(suggestions) < limit:
            remaining = limit - len(suggestions)
            tag_stmt = select(Tag.name, Tag.id).where(
                Tag.user_id == user_id,
                Tag.is_active == True,
                Tag.name.ilike(f"{prefix}%")
            ).limit(remaining)
            
            tag_result = await self.db.execute(tag_stmt)
            tags = tag_result.all()
            
            for name, tag_id in tags:
                suggestions.append(SearchSuggestion(
                    text=name,
                    type="tag",
                    id=tag_id
                ))
        
        # Search in categories
        if len(suggestions) < limit:
            remaining = limit - len(suggestions)
            cat_stmt = select(Category.name, Category.id).where(
                Category.user_id == user_id,
                Category.is_active == True,
                Category.name.ilike(f"{prefix}%")
            ).limit(remaining)
            
            cat_result = await self.db.execute(cat_stmt)
            categories = cat_result.all()
            
            for name, cat_id in categories:
                suggestions.append(SearchSuggestion(
                    text=name,
                    type="category",
                    id=cat_id
                ))
        
        return suggestions
    
    async def get_search_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """
        Get recent search queries for a user.
        Note: This is a placeholder. In production, you'd store search history in a separate table.
        """
        # TODO: Implement search history storage
        return []
    
    async def get_popular_searches(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular search terms.
        Note: This is a placeholder. In production, you'd track search frequency.
        """
        # TODO: Implement search analytics
        return []
    
    async def search_by_similarity(
        self,
        user_id: str,
        knowledge_item_id: str,
        limit: int = 10
    ) -> List[KnowledgeItem]:
        """
        Find similar knowledge items based on tags and category.
        This is a simple similarity search. For production, consider using vector embeddings.
        """
        
        # Get the reference item
        result = await self.db.execute(
            select(KnowledgeItem)
            .options(selectinload(KnowledgeItem.tags))
            .where(
                KnowledgeItem.id == knowledge_item_id,
                KnowledgeItem.author_id == user_id
            )
        )
        reference_item = result.scalar_one_or_none()
        
        if not reference_item:
            return []
        
        # Find items with similar tags or same category
        stmt = select(KnowledgeItem).where(
            KnowledgeItem.author_id == user_id,
            KnowledgeItem.is_deleted == False,
            KnowledgeItem.id != knowledge_item_id
        ).options(
            selectinload(KnowledgeItem.tags),
            selectinload(KnowledgeItem.category)
        )
        
        # Prefer items in same category
        if reference_item.category_id:
            stmt = stmt.where(
                or_(
                    KnowledgeItem.category_id == reference_item.category_id,
                    KnowledgeItem.id.in_(
                        select(KnowledgeItem.id)
                        .join(KnowledgeItem.tags)
                        .where(Tag.id.in_([t.id for t in reference_item.tags]))
                    )
                )
            )
        
        stmt = stmt.limit(limit)
        
        result = await self.db.execute(stmt)
        similar_items = result.scalars().unique().all()
        
        logger.info(f"Similarity search for item {knowledge_item_id}: found {len(similar_items)} similar items")
        return similar_items
