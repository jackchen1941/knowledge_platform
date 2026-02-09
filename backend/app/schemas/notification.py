"""
Notification Schemas

Pydantic schemas for notification operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating notification."""
    title: str = Field(..., max_length=200, description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: str = Field(default="info", pattern="^(info|success|warning|error)$")
    category: str = Field(default="system", pattern="^(sync|knowledge|system|import)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    action_url: Optional[str] = Field(None, max_length=500)
    action_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    expires_hours: Optional[int] = Field(None, ge=1, le=8760)  # Max 1 year
    scheduled_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: str
    title: str
    message: str
    notification_type: str
    category: str
    priority: str
    is_read: bool
    is_archived: bool
    action_url: Optional[str] = None
    action_data: Dict[str, Any]
    created_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response."""
    notifications: List[NotificationResponse]
    total: int
    unread: int
    has_more: bool


class NotificationStatsResponse(BaseModel):
    """Schema for notification statistics."""
    total: int
    unread: int
    categories: Dict[str, int]


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read."""
    notification_ids: Optional[List[str]] = None  # If None, mark all as read
    category: Optional[str] = None  # Filter by category


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    category: str = Field(..., pattern="^(sync|knowledge|system|import)$")
    enabled: bool = True
    in_app: bool = True
    email: bool = False
    push: bool = False
    min_priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""
    id: str
    category: str
    enabled: bool
    in_app: bool
    email: bool
    push: bool
    min_priority: str
    
    class Config:
        from_attributes = True


class NotificationTemplateCreate(BaseModel):
    """Schema for creating notification template."""
    template_key: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    title_template: str = Field(..., max_length=200)
    message_template: str
    notification_type: str = Field(..., pattern="^(info|success|warning|error)$")
    category: str = Field(..., pattern="^(sync|knowledge|system|import)$")
    default_priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    default_expires_hours: Optional[int] = Field(None, ge=1, le=8760)
    variables: List[str] = Field(default_factory=list)


class NotificationTemplateResponse(BaseModel):
    """Schema for notification template response."""
    id: str
    template_key: str
    name: str
    description: Optional[str] = None
    title_template: str
    message_template: str
    notification_type: str
    category: str
    default_priority: str
    default_expires_hours: Optional[int] = None
    variables: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationFromTemplateRequest(BaseModel):
    """Schema for creating notification from template."""
    template_key: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760)
    scheduled_at: Optional[datetime] = None


class BulkNotificationRequest(BaseModel):
    """Schema for sending bulk notifications."""
    user_ids: List[str]
    title: str = Field(..., max_length=200)
    message: str
    notification_type: str = Field(default="info", pattern="^(info|success|warning|error)$")
    category: str = Field(default="system", pattern="^(sync|knowledge|system|import)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760)


class BulkNotificationResponse(BaseModel):
    """Schema for bulk notification response."""
    sent: int
    failed: int
    errors: List[str] = Field(default_factory=list)