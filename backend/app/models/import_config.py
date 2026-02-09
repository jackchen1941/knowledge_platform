"""
Import Configuration Model

Database model for external platform import configurations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class ImportConfig(Base):
    """Import configuration model for external platform integrations."""
    
    __tablename__ = "import_configs"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)  # User-friendly name for the config
    platform = Column(String(50), nullable=False, index=True)  # csdn, wechat, notion, etc.
    
    # Ownership
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Authentication and connection
    credentials = Column(JSON, default=dict, nullable=False)  # API keys, tokens, etc.
    connection_status = Column(String(20), default="inactive")  # active, inactive, error
    last_connection_test = Column(DateTime)
    connection_error = Column(Text)
    
    # Import settings
    import_options = Column(JSON, default=dict, nullable=False)  # Platform-specific options
    auto_import = Column(Boolean, default=False, nullable=False)
    import_schedule = Column(String(100))  # Cron expression for scheduled imports
    
    # Sync tracking
    last_sync = Column(DateTime)
    last_successful_sync = Column(DateTime)
    sync_status = Column(String(20), default="never")  # never, running, success, error
    sync_error = Column(Text)
    total_imported = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Metadata
    meta_data = Column(JSON, default=dict)  # Platform-specific metadata
    
    # Relationships
    user = relationship("User", back_populates="import_configs")
    
    def __repr__(self) -> str:
        return f"<ImportConfig(id={self.id}, name={self.name}, platform={self.platform})>"
    
    @property
    def is_connected(self) -> bool:
        """Check if the configuration is properly connected."""
        return self.connection_status == "active"
    
    @property
    def needs_attention(self) -> bool:
        """Check if the configuration needs user attention."""
        return (
            self.connection_status == "error" or
            self.sync_status == "error" or
            not self.is_active
        )


class ImportTask(Base):
    """Import task model for tracking import operations."""
    
    __tablename__ = "import_tasks"
    
    id = Column(String, primary_key=True)
    config_id = Column(String, ForeignKey("import_configs.id"), nullable=False, index=True)
    
    # Task details
    task_type = Column(String(20), default="manual")  # manual, scheduled, incremental
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Execution details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Results
    import_summary = Column(JSON, default=dict)  # Summary of imported items
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    config = relationship("ImportConfig")
    
    def __repr__(self) -> str:
        return f"<ImportTask(id={self.id}, config_id={self.config_id}, status={self.status})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed (successfully or with errors)."""
        return self.status in ["completed", "failed"]