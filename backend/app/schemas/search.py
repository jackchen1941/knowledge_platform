"""
Search Schemas

Pydantic models for search requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Schema for search query."""
    q: Optional[str] = Field(None, description="Search query string")
    category_id: Optional[str] = Field(None, description="Filter by category")
    tag_ids: Optional[List[str]] = Field(None, description="Filter by tags")
    visibility: Optional[str] = Field(None, pattern="^(private|shared|public)$")
    is_published: Optional[bool] = None
    source_platform: Optional[str] = None
    content_type: Optional[str] = Field(None, pattern="^(markdown|html|plain)$")
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    min_word_count: Optional[int] = Field(None, ge=0)
    max_word_count: Optional[int] = Field(None, ge=0)
    sort_by: str = Field(
        default="updated_at",
        pattern="^(created_at|updated_at|title|view_count|word_count)$"
    )
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchSuggestion(BaseModel):
    """Schema for search suggestion."""
    text: str
    type: str  # 'knowledge_item', 'tag', 'category'
    id: str


class SearchResult(BaseModel):
    """Schema for search result item."""
    id: str
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    category_name: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    word_count: int = 0
    relevance_score: Optional[float] = None
    highlight: Optional[str] = None


class SearchResponse(BaseModel):
    """Schema for search response."""
    results: List[SearchResult]
    total: int
    page: int
    page_size: int
    total_pages: int
    query: str
    took_ms: int


class SearchSuggestionsResponse(BaseModel):
    """Schema for search suggestions response."""
    suggestions: List[SearchSuggestion]


class SearchHistoryResponse(BaseModel):
    """Schema for search history response."""
    queries: List[str]


class PopularSearchItem(BaseModel):
    """Schema for popular search item."""
    query: str
    count: int


class PopularSearchesResponse(BaseModel):
    """Schema for popular searches response."""
    searches: List[PopularSearchItem]


class SimilaritySearchRequest(BaseModel):
    """Schema for similarity search request."""
    knowledge_item_id: str = Field(..., description="Reference knowledge item ID")
    limit: int = Field(default=10, ge=1, le=50)
