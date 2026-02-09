"""
Import Adapter Schemas

Pydantic schemas for import adapter operations.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AdapterConfigBase(BaseModel):
    """Base schema for adapter configuration."""
    name: str = Field(..., description="Configuration name")
    platform: str = Field(..., description="Platform type: csdn, wechat, notion, markdown")
    config: Dict[str, Any] = Field(..., description="Platform-specific configuration")
    auto_sync: bool = Field(default=False, description="Enable automatic sync")
    sync_interval: int = Field(default=3600, description="Sync interval in seconds")


class AdapterConfigCreate(AdapterConfigBase):
    """Schema for creating adapter configuration."""
    pass


class AdapterConfigUpdate(BaseModel):
    """Schema for updating adapter configuration."""
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    auto_sync: Optional[bool] = None
    sync_interval: Optional[int] = None
    is_active: Optional[bool] = None


class AdapterConfigResponse(AdapterConfigBase):
    """Schema for adapter configuration response."""
    id: str
    user_id: str
    is_active: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImportTaskCreate(BaseModel):
    """Schema for creating import task."""
    config_id: str = Field(..., description="Import configuration ID")
    since: Optional[datetime] = Field(None, description="Import items since this date")
    limit: Optional[int] = Field(None, description="Maximum items to import")


class ImportTaskResponse(BaseModel):
    """Schema for import task response."""
    id: str
    config_id: str
    status: str  # pending, running, completed, failed
    items_total: int
    items_imported: int
    items_failed: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImportResult(BaseModel):
    """Schema for import result."""
    success: bool
    items_imported: int
    items_failed: int
    errors: List[str] = []
    task_id: str


class PlatformInfo(BaseModel):
    """Schema for platform information."""
    platform: str
    name: str
    description: str
    required_config: List[str]
    optional_config: List[str] = []
    example_config: Dict[str, Any]


class ValidateConfigRequest(BaseModel):
    """Schema for validating adapter configuration."""
    platform: str
    config: Dict[str, Any]


class ValidateConfigResponse(BaseModel):
    """Schema for configuration validation response."""
    valid: bool
    message: str
    errors: List[str] = []
