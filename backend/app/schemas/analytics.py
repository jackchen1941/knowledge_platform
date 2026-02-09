"""
Analytics Schemas

Pydantic models for analytics requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class OverviewStatsResponse(BaseModel):
    """Schema for overview statistics."""
    total_items: int
    published_items: int
    draft_items: int
    deleted_items: int
    total_words: int
    total_views: int
    total_tags: int
    total_categories: int
    average_words_per_item: int


class RecentActivityResponse(BaseModel):
    """Schema for recent activity statistics."""
    period_days: int
    items_created: int
    items_updated: int
    items_published: int
    total_activity: int


class DistributionItem(BaseModel):
    """Schema for distribution item."""
    name: Optional[str] = None
    type: Optional[str] = None
    count: int


class ContentDistributionResponse(BaseModel):
    """Schema for content distribution."""
    by_category: List[DistributionItem]
    by_content_type: List[DistributionItem]
    by_visibility: List[DistributionItem]


class TopTagItem(BaseModel):
    """Schema for top tag item."""
    name: str
    color: str
    usage_count: int


class TopTagsResponse(BaseModel):
    """Schema for top tags response."""
    tags: List[TopTagItem]


class DailyStatItem(BaseModel):
    """Schema for daily statistics."""
    date: str
    items_created: int
    words_written: int


class WritingTrendsResponse(BaseModel):
    """Schema for writing trends."""
    period_days: int
    daily_stats: List[DailyStatItem]
    total_items: int
    total_words: int
    average_items_per_day: float
    average_words_per_day: float


class WordCountRangeItem(BaseModel):
    """Schema for word count range."""
    range: str
    min_words: int
    max_words: Optional[int]
    count: int


class WordCountDistributionResponse(BaseModel):
    """Schema for word count distribution."""
    distribution: List[WordCountRangeItem]


class SourcePlatformItem(BaseModel):
    """Schema for source platform statistics."""
    platform: str
    count: int


class SourcePlatformStatsResponse(BaseModel):
    """Schema for source platform statistics response."""
    platforms: List[SourcePlatformItem]
