"""
Search Endpoints

Handles search and filtering operations.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.search import SearchService
from app.schemas.search import (
    SearchQuery,
    SearchSuggestionsResponse,
    SearchHistoryResponse,
    PopularSearchesResponse,
    SimilaritySearchRequest
)
from app.schemas.knowledge import KnowledgeListResponse, KnowledgeListItem

router = APIRouter()


@router.get("", response_model=KnowledgeListResponse)
async def search_knowledge(
    q: Optional[str] = Query(None, description="Search query string"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    tag_ids: Optional[List[str]] = Query(None, description="Filter by tags"),
    visibility: Optional[str] = Query(None, description="Filter by visibility"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    source_platform: Optional[str] = Query(None, description="Filter by source platform"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    created_after: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    updated_after: Optional[str] = Query(None, description="Filter by update date (ISO format)"),
    updated_before: Optional[str] = Query(None, description="Filter by update date (ISO format)"),
    min_word_count: Optional[int] = Query(None, ge=0, description="Minimum word count"),
    max_word_count: Optional[int] = Query(None, ge=0, description="Maximum word count"),
    sort_by: str = Query("updated_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search knowledge items with advanced filtering.
    Supports full-text search, category/tag filtering, date ranges, and more.
    """
    
    # Parse datetime strings if provided
    from datetime import datetime
    created_after_dt = datetime.fromisoformat(created_after) if created_after else None
    created_before_dt = datetime.fromisoformat(created_before) if created_before else None
    updated_after_dt = datetime.fromisoformat(updated_after) if updated_after else None
    updated_before_dt = datetime.fromisoformat(updated_before) if updated_before else None
    
    # Build search query
    search_query = SearchQuery(
        q=q,
        category_id=category_id,
        tag_ids=tag_ids,
        visibility=visibility,
        is_published=is_published,
        source_platform=source_platform,
        content_type=content_type,
        created_after=created_after_dt,
        created_before=created_before_dt,
        updated_after=updated_after_dt,
        updated_before=updated_before_dt,
        min_word_count=min_word_count,
        max_word_count=max_word_count,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    service = SearchService(db)
    items, total = await service.search(current_user.id, search_query)
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return KnowledgeListResponse(
        items=[KnowledgeListItem.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    prefix: str = Query(..., min_length=1, description="Search prefix"),
    limit: int = Query(10, ge=1, le=50, description="Number of suggestions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions based on prefix.
    Returns suggestions from knowledge items, tags, and categories.
    """
    service = SearchService(db)
    suggestions = await service.get_suggestions(current_user.id, prefix, limit)
    return SearchSuggestionsResponse(suggestions=suggestions)


@router.get("/history", response_model=SearchHistoryResponse)
async def get_search_history(
    limit: int = Query(10, ge=1, le=50, description="Number of history items"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent search queries for the current user.
    Note: This feature requires search history tracking to be implemented.
    """
    service = SearchService(db)
    queries = await service.get_search_history(current_user.id, limit)
    return SearchHistoryResponse(queries=queries)


@router.get("/popular", response_model=PopularSearchesResponse)
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50, description="Number of popular searches"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular search terms.
    Note: This feature requires search analytics to be implemented.
    """
    service = SearchService(db)
    searches = await service.get_popular_searches(current_user.id, limit)
    return PopularSearchesResponse(searches=searches)


@router.get("/similar/{knowledge_item_id}", response_model=KnowledgeListResponse)
async def find_similar_items(
    knowledge_item_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of similar items"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find knowledge items similar to the specified item.
    Uses tags and category to determine similarity.
    """
    service = SearchService(db)
    items = await service.search_by_similarity(current_user.id, knowledge_item_id, limit)
    
    return KnowledgeListResponse(
        items=[KnowledgeListItem.from_orm(item) for item in items],
        total=len(items),
        page=1,
        page_size=limit,
        total_pages=1
    )
