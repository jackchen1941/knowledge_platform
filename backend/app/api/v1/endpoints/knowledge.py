"""
Knowledge Management Endpoints

Handles CRUD operations for knowledge items.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security, get_current_user_id
from app.services.knowledge import KnowledgeService
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeDraft,
    KnowledgePublish,
    KnowledgeResponse,
    KnowledgeListResponse,
    KnowledgeFilter,
    VersionResponse,
    VersionListResponse,
    VersionCompareRequest,
    VersionCompareResponse,
    VersionRestoreRequest,
    VersionCleanupRequest
)
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

router = APIRouter()


@router.post("", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_item(
    data: KnowledgeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new knowledge item.
    
    - **title**: Title of the knowledge item (required)
    - **content**: Content of the knowledge item (required)
    - **content_type**: Type of content (markdown, html, plain)
    - **summary**: Optional summary
    - **category_id**: Optional category ID
    - **visibility**: Visibility level (private, shared, public)
    - **is_published**: Whether to publish immediately
    - **tag_ids**: List of tag IDs to attach
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.create_knowledge_item(user_id, data)
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge item: {str(e)}"
        )


@router.get("", response_model=KnowledgeListResponse)
async def list_knowledge_items(
    search: str = Query(None, description="Search in title, content, or summary"),
    category_id: str = Query(None, description="Filter by category"),
    tag_ids: str = Query(None, description="Filter by tags (comma-separated)"),
    visibility: str = Query(None, description="Filter by visibility"),
    is_published: bool = Query(None, description="Filter by published status"),
    is_deleted: bool = Query(False, description="Include deleted items"),
    source_platform: str = Query(None, description="Filter by source platform"),
    sort_by: str = Query("updated_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List knowledge items with filtering and pagination.
    
    Returns a paginated list of knowledge items accessible to the current user.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    # Parse tag_ids if provided
    tag_id_list = tag_ids.split(",") if tag_ids else None
    
    filters = KnowledgeFilter(
        search=search,
        category_id=category_id,
        tag_ids=tag_id_list,
        visibility=visibility,
        is_published=is_published,
        is_deleted=is_deleted,
        source_platform=source_platform,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    try:
        result = await service.list_knowledge_items(user_id, filters)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list knowledge items: {str(e)}"
        )


@router.get("/deleted", response_model=KnowledgeListResponse)
async def get_deleted_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get deleted knowledge items (recycle bin).
    
    Returns items that have been soft-deleted and can still be recovered.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        result = await service.get_deleted_items(user_id, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deleted items: {str(e)}"
        )


@router.get("/search", response_model=KnowledgeListResponse)
async def search_knowledge_items(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search knowledge items by title, content, or summary.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        result = await service.search_knowledge_items(user_id, q, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{item_id}", response_model=KnowledgeResponse)
async def get_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific knowledge item by ID.
    
    Increments the view count and returns full item details.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.get_knowledge_item(item_id, user_id)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge item: {str(e)}"
        )


@router.put("/{item_id}", response_model=KnowledgeResponse)
async def update_knowledge_item(
    item_id: str,
    data: KnowledgeUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update a knowledge item.
    
    Creates a new version automatically when content is changed.
    Only the owner can update their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.update_knowledge_item(item_id, user_id, data)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge item: {str(e)}"
        )


@router.post("/{item_id}/draft", response_model=KnowledgeResponse)
async def save_draft(
    item_id: str,
    data: KnowledgeDraft,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Save draft changes to a knowledge item.
    
    This endpoint supports auto-save functionality. It updates the item
    without creating a new version, allowing for frequent saves during editing.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.save_draft(item_id, user_id, data)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save draft: {str(e)}"
        )


@router.post("/{item_id}/publish", response_model=KnowledgeResponse)
async def publish_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Publish a knowledge item.
    
    Marks the item as published and sets the published_at timestamp.
    Creates a version for the publish action.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.publish_knowledge_item(item_id, user_id)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish knowledge item: {str(e)}"
        )


@router.delete("/{item_id}", response_model=KnowledgeResponse)
async def delete_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Soft delete a knowledge item.
    
    Moves the item to the recycle bin. It can be recovered within 30 days.
    Only the owner can delete their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.delete_knowledge_item(item_id, user_id)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge item: {str(e)}"
        )


@router.post("/{item_id}/restore", response_model=KnowledgeResponse)
async def restore_knowledge_item(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Restore a soft-deleted knowledge item.
    
    Recovers an item from the recycle bin if it's within the 30-day recovery period.
    Only the owner can restore their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.restore_knowledge_item(item_id, user_id)
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore knowledge item: {str(e)}"
        )



# Version Control Endpoints

@router.get("/{item_id}/versions", response_model=VersionListResponse)
async def get_versions(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all versions for a knowledge item.
    
    Returns a list of all versions with metadata and content preview.
    Only accessible by the owner or users with read permission.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        result = await service.get_versions(item_id, user_id)
        return result
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get versions: {str(e)}"
        )


@router.get("/{item_id}/versions/{version_id}", response_model=VersionResponse)
async def get_version(
    item_id: str,
    version_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific version by ID.
    
    Returns the full content of a specific version.
    Only accessible by the owner or users with read permission.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        version = await service.get_version(item_id, version_id, user_id)
        return version
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get version: {str(e)}"
        )


@router.post("/{item_id}/versions/{version_id}/restore", response_model=KnowledgeResponse)
async def restore_version(
    item_id: str,
    version_id: str,
    data: VersionRestoreRequest = VersionRestoreRequest(),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Restore a knowledge item to a specific version.
    
    This will:
    1. Create a backup of the current state (if create_backup is True)
    2. Restore the content from the specified version
    3. Create a new version for the restore action
    
    Only the owner can restore their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        item = await service.restore_version(
            item_id, 
            version_id, 
            user_id, 
            create_backup=data.create_backup
        )
        return item
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restore version: {str(e)}"
        )


@router.get("/{item_id}/versions/compare", response_model=VersionCompareResponse)
async def compare_versions(
    item_id: str,
    version_id_1: str = Query(..., description="First version ID to compare"),
    version_id_2: str = Query(..., description="Second version ID to compare"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Compare two versions of a knowledge item.
    
    Returns a detailed diff showing:
    - Title changes
    - Content changes (line-by-line diff)
    - Summary statistics (insertions, deletions, replacements)
    
    Only accessible by the owner or users with read permission.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        result = await service.compare_versions(
            item_id,
            version_id_1,
            version_id_2,
            user_id
        )
        return result
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare versions: {str(e)}"
        )


@router.delete("/{item_id}/versions/{version_id}")
async def delete_version(
    item_id: str,
    version_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a specific version.
    
    This is used for version cleanup. The most recent version cannot be deleted.
    Only the owner can delete versions of their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        await service.delete_version(item_id, version_id, user_id)
        return {"message": "Version deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete version: {str(e)}"
        )


@router.post("/{item_id}/versions/cleanup")
async def cleanup_versions(
    item_id: str,
    data: VersionCleanupRequest = VersionCleanupRequest(),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Clean up old versions of a knowledge item.
    
    This will delete old versions, keeping only the most recent ones.
    The number of versions to keep can be specified (default: 10).
    
    Only the owner can cleanup versions of their knowledge items.
    """
    user_id = get_current_user_id(credentials)
    service = KnowledgeService(db)
    
    try:
        result = await service.cleanup_versions(
            item_id,
            user_id,
            keep_count=data.keep_count
        )
        return result
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup versions: {str(e)}"
        )
