"""
Category Schemas

Pydantic models for category requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class CategoryBase(BaseModel):
    """Base schema for categories."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = Field(0, ge=0)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate category name."""
        if not v or not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = Field(None, ge=0)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate category name if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    user_id: str
    color: str
    icon: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryTreeNode(BaseModel):
    """Schema for category in tree structure."""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    color: str
    icon: Optional[str]
    sort_order: int
    depth: int
    full_path: str
    children: List["CategoryTreeNode"] = []
    
    class Config:
        from_attributes = True


class CategoryListItem(BaseModel):
    """Schema for category in list view."""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    color: str
    icon: Optional[str]
    sort_order: int
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    categories: List[CategoryListItem]
    total: int


class CategoryTreeResponse(BaseModel):
    """Schema for category tree response."""
    tree: List[CategoryTreeNode]
    total: int


class CategoryMoveRequest(BaseModel):
    """Schema for moving a category."""
    new_parent_id: Optional[str] = Field(None, description="New parent category ID (null for root)")


class CategoryMergeRequest(BaseModel):
    """Schema for merging categories."""
    source_category_id: str = Field(..., description="Category to merge from (will be deleted)")
    target_category_id: str = Field(..., description="Category to merge into (will be kept)")


class CategoryStatsResponse(BaseModel):
    """Schema for category statistics."""
    category_id: str
    name: str
    depth: int
    item_count: int
    child_count: int
    descendant_count: int
    full_path: str


# Update forward references
CategoryTreeNode.model_rebuild()
