"""
Backup Schemas

Pydantic schemas for backup and restore operations.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class BackupCreate(BaseModel):
    """Schema for creating a backup."""
    backup_type: str = Field(default="full", description="Backup type: full or incremental")
    since: Optional[datetime] = Field(None, description="For incremental backup: backup changes since this date")


class BackupVerification(BaseModel):
    """Schema for backup verification result."""
    valid: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    item_count: Optional[int] = None
    category_count: Optional[int] = None
    tag_count: Optional[int] = None


class RestoreOptions(BaseModel):
    """Schema for restore options."""
    restore_knowledge: bool = Field(default=True, description="Restore knowledge items")
    restore_categories: bool = Field(default=True, description="Restore categories")
    restore_tags: bool = Field(default=True, description="Restore tags")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing data")


class RestoreResult(BaseModel):
    """Schema for restore result."""
    knowledge_items_restored: int
    categories_restored: int
    tags_restored: int
    errors: list = []
