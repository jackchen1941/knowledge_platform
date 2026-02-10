"""
Category Management Endpoints

Handles CRUD operations for hierarchical categories.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.category import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryTreeResponse,
    CategoryTreeNode,
    CategoryListItem,
    CategoryMoveRequest,
    CategoryMergeRequest,
    CategoryStatsResponse
)

router = APIRouter()


def _build_tree_node(category) -> CategoryTreeNode:
    """Build a tree node from a category with its children."""
    return CategoryTreeNode(
        id=category.id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        color=category.color,
        icon=category.icon,
        sort_order=category.sort_order,
        depth=category.depth,
        full_path=category.full_path,
        children=[_build_tree_node(child) for child in category.children]
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category."""
    service = CategoryService(db)
    category = await service.create_category(current_user_id, data)
    return category


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    parent_id: Optional[str] = Query(None, description="Filter by parent category ID"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List categories, optionally filtered by parent."""
    service = CategoryService(db)
    categories = await service.list_categories(current_user_id, parent_id)
    return CategoryListResponse(
        categories=[CategoryListItem.from_orm(cat) for cat in categories],
        total=len(categories)
    )


@router.get("/tree", response_model=CategoryTreeResponse)
async def get_category_tree(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get full category tree with all descendants."""
    service = CategoryService(db)
    root_categories = await service.get_category_tree(current_user_id)
    tree = [_build_tree_node(cat) for cat in root_categories]
    
    # Count total categories
    total = len(root_categories)
    for cat in root_categories:
        total += len(cat.get_descendants())
    
    return CategoryTreeResponse(tree=tree, total=total)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category by ID."""
    service = CategoryService(db)
    category = await service.get_category(category_id, current_user_id)
    return category


@router.get("/{category_id}/stats", response_model=CategoryStatsResponse)
async def get_category_stats(
    category_id: str,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a category."""
    service = CategoryService(db)
    stats = await service.get_category_stats(category_id, current_user_id)
    return stats


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a category."""
    service = CategoryService(db)
    category = await service.update_category(category_id, current_user_id, data)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    delete_children: bool = Query(False, description="Also delete child categories"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a category (soft delete)."""
    service = CategoryService(db)
    await service.delete_category(category_id, current_user_id, delete_children)
    return None


@router.post("/{category_id}/move", response_model=CategoryResponse)
async def move_category(
    category_id: str,
    data: CategoryMoveRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Move a category to a new parent."""
    service = CategoryService(db)
    category = await service.move_category(category_id, data.new_parent_id, current_user_id)
    return category


@router.post("/merge", response_model=CategoryResponse)
async def merge_categories(
    data: CategoryMergeRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Merge source category into target category."""
    service = CategoryService(db)
    category = await service.merge_categories(
        data.source_category_id,
        data.target_category_id,
        current_user_id
    )
    return category
