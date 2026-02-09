"""
Sync Schemas

Pydantic schemas for synchronization operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DeviceRegister(BaseModel):
    """Schema for device registration."""
    device_name: str = Field(..., description="Device name")
    device_type: str = Field(..., description="Device type: web, mobile, desktop")
    device_id: str = Field(..., description="Unique device identifier")


class DeviceResponse(BaseModel):
    """Schema for device response."""
    id: str
    device_name: str
    device_type: str
    device_id: str
    last_sync: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SyncChangeData(BaseModel):
    """Schema for sync change data."""
    entity_type: str = Field(..., description="Entity type: knowledge, category, tag")
    entity_id: str = Field(..., description="Entity ID")
    operation: str = Field(..., description="Operation: create, update, delete")
    data: Dict[str, Any] = Field(..., description="Change data")
    timestamp: str = Field(..., description="Change timestamp (ISO format)")


class SyncPullRequest(BaseModel):
    """Schema for sync pull request."""
    device_id: str
    last_sync: Optional[datetime] = None


class SyncPullResponse(BaseModel):
    """Schema for sync pull response."""
    changes: Dict[str, List[Dict[str, Any]]]
    sync_time: str
    has_conflicts: bool


class SyncPushRequest(BaseModel):
    """Schema for sync push request."""
    device_id: str
    changes: List[SyncChangeData]


class SyncPushResponse(BaseModel):
    """Schema for sync push response."""
    applied: int
    conflicts: int
    errors: List[str]
    sync_time: str


class ConflictResponse(BaseModel):
    """Schema for conflict response."""
    id: str
    entity_type: str
    entity_id: str
    device1_id: str
    device2_id: str
    device1_data: Dict[str, Any]
    device2_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConflictResolve(BaseModel):
    """Schema for conflict resolution."""
    resolution: str = Field(..., description="Resolution: device1, device2, merge")


class SyncStatsResponse(BaseModel):
    """Schema for sync statistics."""
    total_devices: int
    active_devices: int
    last_sync: Optional[datetime] = None
    pending_changes: int
    unresolved_conflicts: int
