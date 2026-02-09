"""
Analytics Endpoints

Handles statistics and analytics operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.schemas.analytics import (
    OverviewStatsResponse,
    RecentActivityResponse,
    ContentDistributionResponse,
    TopTagsResponse,
    TopTagItem,
    WritingTrendsResponse,
    WordCountDistributionResponse,
    SourcePlatformStatsResponse,
    SourcePlatformItem
)

router = APIRouter()


@router.get("/overview", response_model=OverviewStatsResponse)
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview statistics for the current user.
    Includes total items, words, views, tags, and categories.
    """
    service = AnalyticsService(db)
    stats = await service.get_overview_stats(current_user.id)
    return stats


@router.get("/activity", response_model=RecentActivityResponse)
async def get_recent_activity(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent activity statistics.
    Shows items created, updated, and published in the specified period.
    """
    service = AnalyticsService(db)
    activity = await service.get_recent_activity(current_user.id, days)
    return activity


@router.get("/distribution", response_model=ContentDistributionResponse)
async def get_content_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get content distribution by category, content type, and visibility.
    """
    service = AnalyticsService(db)
    distribution = await service.get_content_distribution(current_user.id)
    return distribution


@router.get("/tags/top", response_model=TopTagsResponse)
async def get_top_tags(
    limit: int = Query(10, ge=1, le=50, description="Number of top tags"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most used tags.
    """
    service = AnalyticsService(db)
    tags = await service.get_top_tags(current_user.id, limit)
    return TopTagsResponse(tags=[TopTagItem(**tag) for tag in tags])


@router.get("/trends", response_model=WritingTrendsResponse)
async def get_writing_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get writing trends over time.
    Shows daily statistics of items created and words written.
    """
    service = AnalyticsService(db)
    trends = await service.get_writing_trends(current_user.id, days)
    return trends


@router.get("/word-count", response_model=WordCountDistributionResponse)
async def get_word_count_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get distribution of items by word count ranges.
    """
    service = AnalyticsService(db)
    distribution = await service.get_word_count_distribution(current_user.id)
    return distribution


@router.get("/sources", response_model=SourcePlatformStatsResponse)
async def get_source_platform_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics by source platform.
    Shows how many items were imported from each platform.
    """
    service = AnalyticsService(db)
    platforms = await service.get_source_platform_stats(current_user.id)
    return SourcePlatformStatsResponse(platforms=[SourcePlatformItem(**p) for p in platforms])
