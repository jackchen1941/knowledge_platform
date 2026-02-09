"""
Attachment Schemas

Pydantic schemas for attachment data validation and serialization.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator


class AttachmentBase(BaseModel):
    """Base attachment schema."""
    filename: str = Field(..., description="Display filename")
    mime_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., ge=0, description="File size in bytes")


class AttachmentCreate(AttachmentBase):
    """Schema for creating an attachment."""
    knowledge_item_id: str = Field(..., description="ID of the knowledge item")
    file_hash: Optional[str] = Field(None, description="SHA-256 hash for deduplication")
    width: Optional[int] = Field(None, ge=0, description="Image/video width")
    height: Optional[int] = Field(None, ge=0, description="Image/video height")
    duration: Optional[int] = Field(None, ge=0, description="Audio/video duration in seconds")


class AttachmentUpdate(BaseModel):
    """Schema for updating an attachment."""
    filename: Optional[str] = Field(None, description="Display filename")
    is_public: Optional[bool] = Field(None, description="Public access flag")


class AttachmentResponse(AttachmentBase):
    """Schema for attachment response."""
    id: str
    original_filename: str
    file_path: str
    file_hash: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    knowledge_item_id: str
    uploaded_by: str
    is_processed: bool
    is_public: bool
    uploaded_at: datetime
    processed_at: Optional[datetime]
    file_size_human: str
    is_image: bool
    is_video: bool
    is_audio: bool
    is_document: bool
    
    class Config:
        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Schema for paginated attachment list."""
    items: List[AttachmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AttachmentUploadResponse(BaseModel):
    """Schema for file upload response."""
    attachment: AttachmentResponse
    message: str = "File uploaded successfully"
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None


class AttachmentBatchUploadResponse(BaseModel):
    """Schema for batch file upload response."""
    attachments: List[AttachmentResponse]
    total_uploaded: int
    total_size: int
    message: str = "Files uploaded successfully"
    duplicates: List[str] = []


class AttachmentStats(BaseModel):
    """Schema for attachment statistics."""
    total_count: int
    total_size: int
    total_size_human: str
    by_type: dict
    by_mime_type: dict
