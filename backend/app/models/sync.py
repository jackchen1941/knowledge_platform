"""
Sync Models

Data models for multi-device synchronization.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class SyncDevice(Base):
    """Device registration for sync."""
    
    __tablename__ = "sync_devices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)  # web, mobile, desktop
    device_id = Column(String(100), unique=True, nullable=False)  # Unique device identifier
    last_sync = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sync_devices")
    sync_logs = relationship("SyncLog", back_populates="device", cascade="all, delete-orphan")


class SyncLog(Base):
    """Sync operation log."""
    
    __tablename__ = "sync_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("sync_devices.id"), nullable=False)
    sync_type = Column(String(20), nullable=False)  # push, pull, full
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    items_synced = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device = relationship("SyncDevice", back_populates="sync_logs")


class SyncChange(Base):
    """Track changes for synchronization."""
    
    __tablename__ = "sync_changes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # knowledge, category, tag, etc.
    entity_id = Column(String(36), nullable=False)
    operation = Column(String(20), nullable=False)  # create, update, delete
    change_data = Column(JSON, nullable=True)  # Changed fields and values
    device_id = Column(String(36), nullable=True)  # Device that made the change
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    synced = Column(Boolean, default=False, index=True)
    
    # Relationships
    user = relationship("User")


class SyncConflict(Base):
    """Track sync conflicts for resolution."""
    
    __tablename__ = "sync_conflicts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    device1_id = Column(String(36), nullable=False)
    device2_id = Column(String(36), nullable=False)
    device1_data = Column(JSON, nullable=False)
    device2_data = Column(JSON, nullable=False)
    resolution = Column(String(20), nullable=True)  # device1, device2, merge, manual
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
