"""
Sync API Endpoints

API endpoints for multi-device synchronization.
"""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.sync import SyncService
from app.schemas.sync import (
    DeviceRegister,
    DeviceResponse,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
    ConflictResponse,
    ConflictResolve,
    SyncStatsResponse,
)

router = APIRouter()


@router.post("/devices/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: DeviceRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a device for synchronization.
    
    Each device must be registered before it can sync data.
    """
    service = SyncService(db)
    
    device = await service.register_device(
        user_id=current_user.id,
        device_name=device_data.device_name,
        device_type=device_data.device_type,
        device_id=device_data.device_id,
    )
    
    return device


@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of registered devices."""
    service = SyncService(db)
    devices = await service.get_devices(current_user.id)
    return devices


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a device."""
    service = SyncService(db)
    await service.deactivate_device(device_id, current_user.id)


@router.post("/pull", response_model=SyncPullResponse)
async def sync_pull(
    request: SyncPullRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pull changes from server.
    
    Returns all changes since last sync.
    """
    service = SyncService(db)
    
    result = await service.sync_pull(
        user_id=current_user.id,
        device_id=request.device_id,
        last_sync=request.last_sync,
    )
    
    return result


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(
    request: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Push changes to server.
    
    Applies changes and detects conflicts.
    """
    service = SyncService(db)
    
    changes = [change.dict() for change in request.changes]
    
    result = await service.sync_push(
        user_id=current_user.id,
        device_id=request.device_id,
        changes=changes,
    )
    
    return result


@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of unresolved conflicts."""
    service = SyncService(db)
    conflicts = await service.get_conflicts(current_user.id)
    return conflicts


@router.post("/conflicts/{conflict_id}/resolve", status_code=status.HTTP_200_OK)
async def resolve_conflict(
    conflict_id: str,
    resolution: ConflictResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a sync conflict."""
    service = SyncService(db)
    
    await service.resolve_conflict(
        conflict_id=conflict_id,
        user_id=current_user.id,
        resolution=resolution.resolution,
    )
    
    return {"message": "Conflict resolved successfully"}


@router.get("/stats", response_model=SyncStatsResponse)
async def get_sync_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get synchronization statistics."""
    service = SyncService(db)
    
    devices = await service.get_devices(current_user.id)
    conflicts = await service.get_conflicts(current_user.id)
    
    # Calculate stats
    total_devices = len(devices)
    active_devices = sum(1 for d in devices if d.is_active)
    last_sync = max([d.last_sync for d in devices if d.last_sync], default=None)
    
    return SyncStatsResponse(
        total_devices=total_devices,
        active_devices=active_devices,
        last_sync=last_sync,
        pending_changes=0,  # TODO: Calculate
        unresolved_conflicts=len(conflicts),
    )
