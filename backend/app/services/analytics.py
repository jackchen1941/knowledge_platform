"""
Analytics Service

Business logic for statistics and analytics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.knowledge import KnowledgeItem
from app.models.tag import Tag
from app.models.category import Category


class AnalyticsService:
    """Service class for analytics operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview_stats(self, user_id: str) -> Dict[str, Any]:
        """Get overview statistics for a user."""
        
        # Total knowledge items
        total_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
        )
        total_items = total_result.scalar()
        
        # Published items
        published_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                KnowledgeItem.is_published == True
            )
        )
        published_items = published_result.scalar()
        
        # Draft items
        draft_items = total_items - published_items
        
        # Deleted items (in recycle bin)
        deleted_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == True
            )
        )
        deleted_items = deleted_result.scalar()
        
        # Total word count
        word_count_result = await self.db.execute(
            select(func.sum(KnowledgeItem.word_count)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
        )
        total_words = word_count_result.scalar() or 0
        
        # Total view count
        view_count_result = await self.db.execute(
            select(func.sum(KnowledgeItem.view_count)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
        )
        total_views = view_count_result.scalar() or 0
        
        # Total tags
        tags_result = await self.db.execute(
            select(func.count(Tag.id)).where(
                Tag.user_id == user_id,
                Tag.is_active == True
            )
        )
        total_tags = tags_result.scalar()
        
        # Total categories
        categories_result = await self.db.execute(
            select(func.count(Category.id)).where(
                Category.user_id == user_id,
                Category.is_active == True
            )
        )
        total_categories = categories_result.scalar()
        
        return {
            "total_items": total_items,
            "published_items": published_items,
            "draft_items": draft_items,
            "deleted_items": deleted_items,
            "total_words": total_words,
            "total_views": total_views,
            "total_tags": total_tags,
            "total_categories": total_categories,
            "average_words_per_item": int(total_words / total_items) if total_items > 0 else 0
        }
    
    async def get_recent_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get recent activity statistics."""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Items created in period
        created_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.created_at >= since
            )
        )
        items_created = created_result.scalar()
        
        # Items updated in period
        updated_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.updated_at >= since,
                KnowledgeItem.created_at < since  # Exclude newly created
            )
        )
        items_updated = updated_result.scalar()
        
        # Items published in period
        published_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.published_at >= since
            )
        )
        items_published = published_result.scalar()
        
        return {
            "period_days": days,
            "items_created": items_created,
            "items_updated": items_updated,
            "items_published": items_published,
            "total_activity": items_created + items_updated
        }
    
    async def get_content_distribution(self, user_id: str) -> Dict[str, Any]:
        """Get content distribution by category and tags."""
        
        # Distribution by category
        category_result = await self.db.execute(
            select(
                Category.name,
                func.count(KnowledgeItem.id).label('count')
            )
            .join(KnowledgeItem, KnowledgeItem.category_id == Category.id)
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
            .group_by(Category.id, Category.name)
            .order_by(func.count(KnowledgeItem.id).desc())
            .limit(10)
        )
        categories = [
            {"name": row[0], "count": row[1]}
            for row in category_result.all()
        ]
        
        # Items without category
        no_category_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                KnowledgeItem.category_id.is_(None)
            )
        )
        no_category_count = no_category_result.scalar()
        
        if no_category_count > 0:
            categories.append({"name": "未分类", "count": no_category_count})
        
        # Distribution by content type
        content_type_result = await self.db.execute(
            select(
                KnowledgeItem.content_type,
                func.count(KnowledgeItem.id).label('count')
            )
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
            .group_by(KnowledgeItem.content_type)
        )
        content_types = [
            {"type": row[0], "count": row[1]}
            for row in content_type_result.all()
        ]
        
        # Distribution by visibility
        visibility_result = await self.db.execute(
            select(
                KnowledgeItem.visibility,
                func.count(KnowledgeItem.id).label('count')
            )
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False
            )
            .group_by(KnowledgeItem.visibility)
        )
        visibility = [
            {"type": row[0], "count": row[1]}
            for row in visibility_result.all()
        ]
        
        return {
            "by_category": categories,
            "by_content_type": content_types,
            "by_visibility": visibility
        }
    
    async def get_top_tags(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most used tags."""
        
        result = await self.db.execute(
            select(Tag.name, Tag.color, Tag.usage_count)
            .where(
                Tag.user_id == user_id,
                Tag.is_active == True,
                Tag.usage_count > 0
            )
            .order_by(Tag.usage_count.desc())
            .limit(limit)
        )
        
        return [
            {
                "name": row[0],
                "color": row[1],
                "usage_count": row[2]
            }
            for row in result.all()
        ]
    
    async def get_writing_trends(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get writing trends over time."""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get items created per day
        result = await self.db.execute(
            select(
                func.date(KnowledgeItem.created_at).label('date'),
                func.count(KnowledgeItem.id).label('count'),
                func.sum(KnowledgeItem.word_count).label('words')
            )
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.created_at >= since
            )
            .group_by(func.date(KnowledgeItem.created_at))
            .order_by(func.date(KnowledgeItem.created_at))
        )
        
        daily_stats = [
            {
                "date": row[0].isoformat() if row[0] else None,
                "items_created": row[1],
                "words_written": row[2] or 0
            }
            for row in result.all()
        ]
        
        # Calculate totals
        total_items = sum(day["items_created"] for day in daily_stats)
        total_words = sum(day["words_written"] for day in daily_stats)
        
        return {
            "period_days": days,
            "daily_stats": daily_stats,
            "total_items": total_items,
            "total_words": total_words,
            "average_items_per_day": round(total_items / days, 2) if days > 0 else 0,
            "average_words_per_day": round(total_words / days, 2) if days > 0 else 0
        }
    
    async def get_word_count_distribution(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get distribution of items by word count ranges."""
        
        ranges = [
            (0, 500, "短文 (0-500字)"),
            (501, 1000, "中等 (501-1000字)"),
            (1001, 2000, "长文 (1001-2000字)"),
            (2001, 5000, "很长 (2001-5000字)"),
            (5001, None, "超长 (5000字以上)")
        ]
        
        distribution = []
        
        for min_words, max_words, label in ranges:
            query = select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                KnowledgeItem.word_count >= min_words
            )
            
            if max_words:
                query = query.where(KnowledgeItem.word_count <= max_words)
            
            result = await self.db.execute(query)
            count = result.scalar()
            
            distribution.append({
                "range": label,
                "min_words": min_words,
                "max_words": max_words,
                "count": count
            })
        
        return {"distribution": distribution}
    
    async def get_source_platform_stats(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get statistics by source platform."""
        
        result = await self.db.execute(
            select(
                KnowledgeItem.source_platform,
                func.count(KnowledgeItem.id).label('count')
            )
            .where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                KnowledgeItem.source_platform.isnot(None)
            )
            .group_by(KnowledgeItem.source_platform)
            .order_by(func.count(KnowledgeItem.id).desc())
        )
        
        platforms = [
            {
                "platform": row[0],
                "count": row[1]
            }
            for row in result.all()
        ]
        
        # Add original content count
        original_result = await self.db.execute(
            select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.author_id == user_id,
                KnowledgeItem.is_deleted == False,
                KnowledgeItem.source_platform.is_(None)
            )
        )
        original_count = original_result.scalar()
        
        if original_count > 0:
            platforms.insert(0, {
                "platform": "原创",
                "count": original_count
            })
        
        return platforms
