"""
Tag Management Endpoints

Handles CRUD operations for tags.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.tag import TagService
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
    TagMergeRequest,
    TagAutocompleteResponse,
    TagListItem
)

router = APIRouter()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag."""
    service = TagService(db)
    tag = await service.create_tag(current_user.id, data)
    return tag


@router.get("", response_model=TagListResponse)
async def list_tags(
    search: Optional[str] = Query(None, description="Search tags by name"),
    include_system: bool = Query(True, description="Include system tags"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all tags for the current user."""
    service = TagService(db)
    tags = await service.list_tags(current_user.id, search, include_system)
    return TagListResponse(tags=[TagListItem.from_orm(tag) for tag in tags], total=len(tags))


@router.get("/popular", response_model=TagListResponse)
async def get_popular_tags(
    limit: int = Query(10, ge=1, le=50, description="Number of tags to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get most popular tags by usage count."""
    service = TagService(db)
    tags = await service.get_popular_tags(current_user.id, limit)
    return TagListResponse(tags=[TagListItem.from_orm(tag) for tag in tags], total=len(tags))


@router.get("/autocomplete", response_model=TagAutocompleteResponse)
async def autocomplete_tags(
    prefix: str = Query(..., min_length=1, description="Tag name prefix"),
    limit: int = Query(10, ge=1, le=50, description="Number of suggestions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Autocomplete tag names based on prefix."""
    service = TagService(db)
    tags = await service.autocomplete_tags(current_user.id, prefix, limit)
    return TagAutocompleteResponse(suggestions=[TagListItem.from_orm(tag) for tag in tags])


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tag by ID."""
    service = TagService(db)
    tag = await service.get_tag(tag_id, current_user.id)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a tag."""
    service = TagService(db)
    tag = await service.update_tag(tag_id, current_user.id, data)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a tag (soft delete)."""
    service = TagService(db)
    await service.delete_tag(tag_id, current_user.id)
    return None


@router.post("/merge", response_model=TagResponse)
async def merge_tags(
    data: TagMergeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Merge source tag into target tag."""
    service = TagService(db)
    tag = await service.merge_tags(data.source_tag_id, data.target_tag_id, current_user.id)
    return tag