"""
Sync Service

Business logic for multi-device synchronization.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from app.models.sync import SyncDevice, SyncLog, SyncChange, SyncConflict
from app.models.knowledge import KnowledgeItem
from app.models.category import Category
from app.models.tag import Tag
from app.core.exceptions import NotFoundError, ValidationError


class SyncService:
    """Service class for multi-device synchronization."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_device(
        self,
        user_id: str,
        device_name: str,
        device_type: str,
        device_id: str
    ) -> SyncDevice:
        """Register a new device for sync."""
        
        # Check if device already exists
        result = await self.db.execute(
            select(SyncDevice).where(SyncDevice.device_id == device_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing device
            existing.device_name = device_name
            existing.device_type = device_type
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        
        # Create new device
        device = SyncDevice(
            id=str(uuid.uuid4()),
            user_id=user_id,
            device_name=device_name,
            device_type=device_type,
            device_id=device_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        
        logger.info(f"Device registered: {device_name} ({device_type})")
        return device
    
    async def get_devices(self, user_id: str) -> List[SyncDevice]:
        """Get all devices for a user."""
        
        result = await self.db.execute(
            select(SyncDevice).where(
                SyncDevice.user_id == user_id,
                SyncDevice.is_active == True
            ).order_by(SyncDevice.last_sync.desc())
        )
        return result.scalars().all()
    
    async def deactivate_device(self, device_id: str, user_id: str) -> bool:
        """Deactivate a device."""
        
        result = await self.db.execute(
            select(SyncDevice).where(
                SyncDevice.id == device_id,
                SyncDevice.user_id == user_id
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            raise NotFoundError("Device not found")
        
        device.is_active = False
        device.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Device deactivated: {device.device_name}")
        return True
    
    async def get_changes(
        self,
        user_id: str,
        since: datetime,
        device_id: Optional[str] = None
    ) -> List[SyncChange]:
        """Get changes since a specific time."""
        
        query = select(SyncChange).where(
            SyncChange.user_id == user_id,
            SyncChange.timestamp > since
        )
        
        # Exclude changes from the requesting device
        if device_id:
            query = query.where(SyncChange.device_id != device_id)
        
        query = query.order_by(SyncChange.timestamp.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def record_change(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        operation: str,
        change_data: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> SyncChange:
        """Record a change for synchronization."""
        
        change = SyncChange(
            id=str(uuid.uuid4()),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            change_data=change_data,
            device_id=device_id,
            timestamp=datetime.utcnow(),
            synced=False,
        )
        
        self.db.add(change)
        await self.db.commit()
        await self.db.refresh(change)
        
        return change
    
    async def sync_pull(
        self,
        user_id: str,
        device_id: str,
        last_sync: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Pull changes from server to device.
        
        Returns all changes since last sync.
        """
        
        # Get device
        result = await self.db.execute(
            select(SyncDevice).where(
                SyncDevice.id == device_id,
                SyncDevice.user_id == user_id
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            raise NotFoundError("Device not found")
        
        # Use last_sync from device if not provided
        if not last_sync:
            last_sync = device.last_sync or datetime.utcnow() - timedelta(days=30)
        
        # Get changes
        changes = await self.get_changes(user_id, last_sync, device_id)
        
        # Group changes by entity type
        grouped_changes = {
            'knowledge': [],
            'categories': [],
            'tags': [],
        }
        
        for change in changes:
            if change.entity_type in grouped_changes:
                grouped_changes[change.entity_type].append({
                    'id': change.entity_id,
                    'operation': change.operation,
                    'data': change.change_data,
                    'timestamp': change.timestamp.isoformat(),
                })
        
        # Update device last_sync
        device.last_sync = datetime.utcnow()
        await self.db.commit()
        
        return {
            'changes': grouped_changes,
            'sync_time': datetime.utcnow().isoformat(),
            'has_conflicts': False,  # TODO: Implement conflict detection
        }
    
    async def sync_push(
        self,
        user_id: str,
        device_id: str,
        changes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Push changes from device to server.
        
        Applies changes and detects conflicts.
        """
        
        applied = 0
        conflicts = 0
        errors = []
        
        for change in changes:
            try:
                # Check for conflicts
                has_conflict = await self._check_conflict(
                    user_id,
                    change['entity_type'],
                    change['entity_id'],
                    change['timestamp'],
                    device_id
                )
                
                if has_conflict:
                    conflicts += 1
                    # Record conflict for manual resolution
                    await self._record_conflict(
                        user_id,
                        change['entity_type'],
                        change['entity_id'],
                        device_id,
                        change['data']
                    )
                    continue
                
                # Apply change
                await self._apply_change(
                    user_id,
                    change['entity_type'],
                    change['entity_id'],
                    change['operation'],
                    change['data']
                )
                
                # Record change
                await self.record_change(
                    user_id,
                    change['entity_type'],
                    change['entity_id'],
                    change['operation'],
                    change['data'],
                    device_id
                )
                
                applied += 1
            
            except Exception as e:
                logger.error(f"Error applying change: {str(e)}")
                errors.append(str(e))
        
        return {
            'applied': applied,
            'conflicts': conflicts,
            'errors': errors,
            'sync_time': datetime.utcnow().isoformat(),
        }
    
    async def _check_conflict(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        change_timestamp: str,
        device_id: str
    ) -> bool:
        """Check if there's a conflict with existing changes."""
        
        timestamp = datetime.fromisoformat(change_timestamp)
        
        # Check for newer changes from other devices
        result = await self.db.execute(
            select(SyncChange).where(
                SyncChange.user_id == user_id,
                SyncChange.entity_type == entity_type,
                SyncChange.entity_id == entity_id,
                SyncChange.device_id != device_id,
                SyncChange.timestamp > timestamp
            )
        )
        
        newer_changes = result.scalars().all()
        return len(newer_changes) > 0
    
    async def _record_conflict(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        device_id: str,
        device_data: Dict[str, Any]
    ) -> None:
        """Record a sync conflict."""
        
        # Get current server data
        server_data = await self._get_entity_data(entity_type, entity_id)
        
        conflict = SyncConflict(
            id=str(uuid.uuid4()),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            device1_id=device_id,
            device2_id='server',
            device1_data=device_data,
            device2_data=server_data,
            resolved=False,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(conflict)
        await self.db.commit()
    
    async def _apply_change(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        operation: str,
        data: Dict[str, Any]
    ) -> None:
        """Apply a change to the database."""
        
        if entity_type == 'knowledge':
            await self._apply_knowledge_change(user_id, entity_id, operation, data)
        elif entity_type == 'category':
            await self._apply_category_change(user_id, entity_id, operation, data)
        elif entity_type == 'tag':
            await self._apply_tag_change(user_id, entity_id, operation, data)
    
    async def _apply_knowledge_change(
        self,
        user_id: str,
        entity_id: str,
        operation: str,
        data: Dict[str, Any]
    ) -> None:
        """Apply knowledge item change."""
        
        if operation == 'create':
            item = KnowledgeItem(**data)
            self.db.add(item)
        
        elif operation == 'update':
            result = await self.db.execute(
                select(KnowledgeItem).where(KnowledgeItem.id == entity_id)
            )
            item = result.scalar_one_or_none()
            if item:
                for key, value in data.items():
                    setattr(item, key, value)
        
        elif operation == 'delete':
            result = await self.db.execute(
                select(KnowledgeItem).where(KnowledgeItem.id == entity_id)
            )
            item = result.scalar_one_or_none()
            if item:
                item.is_deleted = True
                item.deleted_at = datetime.utcnow()
        
        await self.db.commit()
    
    async def _apply_category_change(
        self,
        user_id: str,
        entity_id: str,
        operation: str,
        data: Dict[str, Any]
    ) -> None:
        """Apply category change."""
        # Similar to knowledge change
        pass
    
    async def _apply_tag_change(
        self,
        user_id: str,
        entity_id: str,
        operation: str,
        data: Dict[str, Any]
    ) -> None:
        """Apply tag change."""
        # Similar to knowledge change
        pass
    
    async def _get_entity_data(
        self,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """Get current entity data from database."""
        
        if entity_type == 'knowledge':
            result = await self.db.execute(
                select(KnowledgeItem).where(KnowledgeItem.id == entity_id)
            )
            item = result.scalar_one_or_none()
            if item:
                return {
                    'title': item.title,
                    'content': item.content,
                    'updated_at': item.updated_at.isoformat(),
                }
        
        return {}
    
    async def get_conflicts(self, user_id: str) -> List[SyncConflict]:
        """Get unresolved conflicts for a user."""
        
        result = await self.db.execute(
            select(SyncConflict).where(
                SyncConflict.user_id == user_id,
                SyncConflict.resolved == False
            ).order_by(SyncConflict.created_at.desc())
        )
        return result.scalars().all()
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        user_id: str,
        resolution: str
    ) -> bool:
        """Resolve a sync conflict."""
        
        result = await self.db.execute(
            select(SyncConflict).where(
                SyncConflict.id == conflict_id,
                SyncConflict.user_id == user_id
            )
        )
        conflict = result.scalar_one_or_none()
        
        if not conflict:
            raise NotFoundError("Conflict not found")
        
        # Apply resolution
        if resolution == 'device1':
            await self._apply_change(
                user_id,
                conflict.entity_type,
                conflict.entity_id,
                'update',
                conflict.device1_data
            )
        elif resolution == 'device2':
            await self._apply_change(
                user_id,
                conflict.entity_type,
                conflict.entity_id,
                'update',
                conflict.device2_data
            )
        
        # Mark as resolved
        conflict.resolved = True
        conflict.resolution = resolution
        conflict.resolved_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(f"Conflict resolved: {conflict_id} with {resolution}")
        return True
