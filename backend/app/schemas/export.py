"""
Export Schemas

Pydantic models for export requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExportSingleRequest(BaseModel):
    """Schema for exporting a single item."""
    format: str = Field(..., pattern="^(markdown|json|html)$", description="Export format")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    include_versions: bool = Field(default=False, description="Include version history (JSON only)")


class ExportBatchRequest(BaseModel):
    """Schema for batch export."""
    item_ids: List[str] = Field(..., min_items=1, description="List of knowledge item IDs")
    format: str = Field(default="markdown", pattern="^(markdown|json|html)$")
    include_metadata: bool = Field(default=True, description="Include metadata in export")


class ExportAllRequest(BaseModel):
    """Schema for exporting all items."""
    format: str = Field(default="json", pattern="^(markdown|json|html)$")
    include_deleted: bool = Field(default=False, description="Include deleted items")


class ExportResponse(BaseModel):
    """Schema for export response."""
    message: str
    filename: str
    format: str
    item_count: int
