"""
Knowledge Item Schemas

Pydantic models for knowledge item requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class KnowledgeBase(BaseModel):
    """Base schema for knowledge items."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="markdown", pattern="^(markdown|html|plain)$")
    summary: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[str] = None
    visibility: str = Field(default="private", pattern="^(private|shared|public)$")
    source_platform: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = Field(None, max_length=1000)
    source_id: Optional[str] = Field(None, max_length=255)
    meta_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tag_ids: Optional[List[str]] = Field(default_factory=list)


class KnowledgeCreate(KnowledgeBase):
    """Schema for creating a knowledge item."""
    is_published: bool = Field(default=False)
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v


class KnowledgeUpdate(BaseModel):
    """Schema for updating a knowledge item."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, pattern="^(markdown|html|plain)$")
    summary: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[str] = None
    visibility: Optional[str] = Field(None, pattern="^(private|shared|public)$")
    source_platform: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = Field(None, max_length=1000)
    meta_data: Optional[Dict[str, Any]] = None
    tag_ids: Optional[List[str]] = None
    change_summary: Optional[str] = Field(None, max_length=500)
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content is not empty if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Content cannot be empty')
        return v


class KnowledgeDraft(BaseModel):
    """Schema for saving a draft."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    content_type: Optional[str] = Field(None, pattern="^(markdown|html|plain)$")
    summary: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    tag_ids: Optional[List[str]] = None


class KnowledgePublish(BaseModel):
    """Schema for publishing a knowledge item."""
    publish: bool = True


class TagResponse(BaseModel):
    """Schema for tag response."""
    id: str
    name: str
    color: str
    usage_count: int
    
    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: str
    name: str
    description: Optional[str]
    color: str
    icon: Optional[str]
    parent_id: Optional[str]
    
    class Config:
        from_attributes = True


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""
    id: str
    filename: str
    original_filename: str
    file_path: str
    mime_type: str
    file_size: int
    file_size_human: str
    is_image: bool
    is_video: bool
    is_audio: bool
    is_document: bool
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class VersionResponse(BaseModel):
    """Schema for version response."""
    id: str
    version_number: int
    title: str
    content: str
    content_type: str
    change_summary: Optional[str]
    change_type: str
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class VersionListItem(BaseModel):
    """Schema for version in list view (without full content)."""
    id: str
    version_number: int
    title: str
    change_summary: Optional[str]
    change_type: str
    created_by: str
    created_at: datetime
    content_preview: str  # First 200 characters
    
    class Config:
        from_attributes = True


class VersionListResponse(BaseModel):
    """Schema for version list response."""
    versions: List[VersionListItem]
    total: int
    knowledge_item_id: str


class VersionCompareRequest(BaseModel):
    """Schema for version comparison request."""
    version_id_1: str
    version_id_2: str


class VersionDiff(BaseModel):
    """Schema for version difference."""
    operation: str  # 'equal', 'insert', 'delete', 'replace'
    old_start: int
    old_end: int
    new_start: int
    new_end: int
    old_text: Optional[str]
    new_text: Optional[str]


class VersionCompareResponse(BaseModel):
    """Schema for version comparison response."""
    version_1: VersionResponse
    version_2: VersionResponse
    title_diff: List[VersionDiff]
    content_diff: List[VersionDiff]
    summary: Dict[str, int]  # Statistics about changes


class VersionRestoreRequest(BaseModel):
    """Schema for version restore request."""
    create_backup: bool = Field(default=True, description="Create backup before restore")


class VersionCleanupRequest(BaseModel):
    """Schema for version cleanup request."""
    keep_count: int = Field(default=10, ge=1, le=100, description="Number of recent versions to keep")
    compress_old: bool = Field(default=True, description="Compress old versions")


class KnowledgeResponse(BaseModel):
    """Schema for knowledge item response."""
    id: str
    title: str
    content: str
    content_type: str
    summary: Optional[str]
    author_id: str
    category_id: Optional[str]
    category: Optional[CategoryResponse]
    source_platform: Optional[str]
    source_url: Optional[str]
    source_id: Optional[str]
    is_published: bool
    is_deleted: bool
    visibility: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    deleted_at: Optional[datetime]
    meta_data: Dict[str, Any]
    view_count: int
    word_count: int
    reading_time: int
    tags: List[TagResponse]
    attachments: List[AttachmentResponse]
    is_recoverable: bool
    days_until_permanent_deletion: int
    
    class Config:
        from_attributes = True


class KnowledgeListItem(BaseModel):
    """Schema for knowledge item in list view (lighter response)."""
    id: str
    title: str
    summary: Optional[str]
    content_type: str
    author_id: str
    category_id: Optional[str]
    category: Optional[CategoryResponse]
    is_published: bool
    is_deleted: bool
    visibility: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    view_count: int
    word_count: int
    reading_time: int
    tags: List[TagResponse]
    
    class Config:
        from_attributes = True


class KnowledgeListResponse(BaseModel):
    """Schema for paginated knowledge list response."""
    items: List[KnowledgeListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class KnowledgeFilter(BaseModel):
    """Schema for filtering knowledge items."""
    search: Optional[str] = None
    category_id: Optional[str] = None
    tag_ids: Optional[List[str]] = None
    visibility: Optional[str] = None
    is_published: Optional[bool] = None
    is_deleted: Optional[bool] = False
    source_platform: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    sort_by: str = Field(default="updated_at", pattern="^(created_at|updated_at|title|view_count|word_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
