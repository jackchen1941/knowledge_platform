"""
Tag Schemas

Pydantic models for tag requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class TagBase(BaseModel):
    """Base schema for tags."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate tag name."""
        if not v or not v.strip():
            raise ValueError('Tag name cannot be empty')
        return v.strip()


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate tag name if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Tag name cannot be empty')
        return v.strip() if v else v


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: str
    name: str
    description: Optional[str]
    color: str
    user_id: str
    usage_count: int
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TagListItem(BaseModel):
    """Schema for tag in list view."""
    id: str
    name: str
    description: Optional[str]
    color: str
    usage_count: int
    is_system: bool
    
    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for tag list response."""
    tags: List[TagListItem]
    total: int


class TagMergeRequest(BaseModel):
    """Schema for merging tags."""
    source_tag_id: str = Field(..., description="Tag to merge from (will be deleted)")
    target_tag_id: str = Field(..., description="Tag to merge into (will be kept)")


class TagAutocompleteResponse(BaseModel):
    """Schema for tag autocomplete response."""
    suggestions: List[TagListItem]
