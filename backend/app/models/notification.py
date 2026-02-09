"""
Notification Models

Database models for real-time notifications and messaging.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    """Notification model for user notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, index=True)  # info, success, warning, error
    category = Column(String(50), nullable=False, index=True)  # sync, knowledge, system, import
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Priority and scheduling
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    scheduled_at = Column(DateTime, nullable=True)  # For scheduled notifications
    expires_at = Column(DateTime, nullable=True)  # Auto-expire notifications
    
    # Action and metadata
    action_url = Column(String(500), nullable=True)  # URL to navigate when clicked
    action_data = Column(JSON, default=dict)  # Additional action data
    extra_data = Column(JSON, default=dict)  # Extra notification data (renamed from metadata)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.notification_type})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future."""
        if not self.scheduled_at:
            return False
        return datetime.utcnow() < self.scheduled_at


class NotificationTemplate(Base):
    """Template for generating notifications."""
    
    __tablename__ = "notification_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Template identification
    template_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template content
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    
    # Default settings
    default_priority = Column(String(20), default="normal")
    default_expires_hours = Column(Integer, nullable=True)  # Hours until expiration
    
    # Template metadata
    variables = Column(JSON, default=list)  # List of template variables
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<NotificationTemplate(key={self.template_key}, name={self.name})>"


class NotificationPreference(Base):
    """User notification preferences."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Preference settings
    category = Column(String(50), nullable=False, index=True)  # sync, knowledge, system, import
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Delivery preferences
    in_app = Column(Boolean, default=True, nullable=False)  # Show in app notifications
    email = Column(Boolean, default=False, nullable=False)  # Send email notifications
    push = Column(Boolean, default=False, nullable=False)  # Send push notifications
    
    # Timing preferences
    quiet_hours_start = Column(String(5), nullable=True)  # "22:00" format
    quiet_hours_end = Column(String(5), nullable=True)  # "08:00" format
    timezone = Column(String(50), default="UTC")
    
    # Priority filtering
    min_priority = Column(String(20), default="normal")  # Only show notifications >= this priority
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self) -> str:
        return f"<NotificationPreference(user_id={self.user_id}, category={self.category})>"


class NotificationDelivery(Base):
    """Track notification delivery attempts."""
    
    __tablename__ = "notification_deliveries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(String(36), ForeignKey("notifications.id"), nullable=False, index=True)
    
    # Delivery details
    delivery_method = Column(String(20), nullable=False)  # in_app, email, push
    status = Column(String(20), nullable=False)  # pending, sent, delivered, failed
    
    # Delivery tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # External tracking
    external_id = Column(String(200), nullable=True)  # External service message ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    notification = relationship("Notification")
    
    def __repr__(self) -> str:
        return f"<NotificationDelivery(notification_id={self.notification_id}, method={self.delivery_method})>"
    
    @property
    def can_retry(self) -> bool:
        """Check if delivery can be retried."""
        return self.retry_count < self.max_retries and self.status == "failed"