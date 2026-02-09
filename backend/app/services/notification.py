"""
Notification Service

Service for managing real-time notifications and messaging.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload

from app.models.notification import (
    Notification, 
    NotificationTemplate, 
    NotificationPreference,
    NotificationDelivery
)
from app.models.user import User


class NotificationService:
    """Service for notification management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "system",
        priority: str = "normal",
        action_url: Optional[str] = None,
        action_data: Optional[Dict[str, Any]] = None,
        expires_hours: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        send_realtime: bool = True
    ) -> Notification:
        """Create a new notification."""
        
        # Calculate expiration time
        expires_at = None
        if expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            priority=priority,
            action_url=action_url,
            action_data=action_data or {},
            expires_at=expires_at,
            scheduled_at=scheduled_at
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        # Schedule delivery if not scheduled for future
        if not scheduled_at or scheduled_at <= datetime.utcnow():
            await self._schedule_delivery(notification)
        
        # Send real-time notification via WebSocket
        if send_realtime and (not scheduled_at or scheduled_at <= datetime.utcnow()):
            await self._send_realtime_notification(notification)
        
        return notification
    
    async def create_from_template(
        self,
        user_id: str,
        template_key: str,
        variables: Dict[str, Any],
        **kwargs
    ) -> Notification:
        """Create notification from template."""
        
        # Get template
        result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.template_key == template_key,
                    NotificationTemplate.is_active == True
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"Template not found: {template_key}")
        
        # Render template
        title = self._render_template(template.title_template, variables)
        message = self._render_template(template.message_template, variables)
        
        # Use template defaults if not overridden
        notification_type = kwargs.get('notification_type', template.notification_type)
        category = kwargs.get('category', template.category)
        priority = kwargs.get('priority', template.default_priority)
        
        # Calculate expiration from template
        expires_hours = kwargs.get('expires_hours', template.default_expires_hours)
        
        return await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            priority=priority,
            expires_hours=expires_hours,
            **{k: v for k, v in kwargs.items() if k not in ['notification_type', 'category', 'priority', 'expires_hours']}
        )
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get user notifications."""
        
        query = select(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_archived == False,
                or_(
                    Notification.expires_at.is_(None),
                    Notification.expires_at > datetime.utcnow()
                )
            )
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        if category:
            query = query.where(Notification.category == category)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read."""
        
        result = await self.db.execute(
            update(Notification)
            .where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow()
            )
        )
        
        await self.db.commit()
        return result.rowcount > 0
    
    async def mark_all_as_read(self, user_id: str, category: Optional[str] = None) -> int:
        """Mark all notifications as read."""
        
        query = update(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        if category:
            query = query.where(Notification.category == category)
        
        query = query.values(
            is_read=True,
            read_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount
    
    async def archive_notification(self, notification_id: str, user_id: str) -> bool:
        """Archive notification."""
        
        result = await self.db.execute(
            update(Notification)
            .where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .values(
                is_archived=True,
                archived_at=datetime.utcnow()
            )
        )
        
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics."""
        
        # Total notifications
        total_result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_archived == False
                )
            )
        )
        total = len(total_result.scalars().all())
        
        # Unread notifications
        unread_result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                    Notification.is_archived == False
                )
            )
        )
        unread = len(unread_result.scalars().all())
        
        # By category
        categories = {}
        for category in ['sync', 'knowledge', 'system', 'import']:
            cat_result = await self.db.execute(
                select(Notification).where(
                    and_(
                        Notification.user_id == user_id,
                        Notification.category == category,
                        Notification.is_read == False,
                        Notification.is_archived == False
                    )
                )
            )
            categories[category] = len(cat_result.scalars().all())
        
        return {
            'total': total,
            'unread': unread,
            'categories': categories
        }
    
    async def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications."""
        
        result = await self.db.execute(
            delete(Notification).where(
                and_(
                    Notification.expires_at.is_not(None),
                    Notification.expires_at < datetime.utcnow()
                )
            )
        )
        
        await self.db.commit()
        return result.rowcount
    
    async def _schedule_delivery(self, notification: Notification):
        """Schedule notification delivery."""
        
        # Get user preferences
        prefs_result = await self.db.execute(
            select(NotificationPreference).where(
                and_(
                    NotificationPreference.user_id == notification.user_id,
                    NotificationPreference.category == notification.category
                )
            )
        )
        prefs = prefs_result.scalar_one_or_none()
        
        # Use default preferences if none found
        if not prefs:
            prefs = NotificationPreference(
                user_id=notification.user_id,
                category=notification.category,
                in_app=True,
                email=False,
                push=False
            )
        
        # Check if notification should be delivered based on preferences
        if not prefs.enabled:
            return
        
        # Check priority filtering
        priority_levels = {'low': 0, 'normal': 1, 'high': 2, 'urgent': 3}
        if priority_levels.get(notification.priority, 1) < priority_levels.get(prefs.min_priority, 1):
            return
        
        # Schedule delivery methods
        if prefs.in_app:
            await self._create_delivery(notification.id, 'in_app')
        
        if prefs.email:
            await self._create_delivery(notification.id, 'email')
        
        if prefs.push:
            await self._create_delivery(notification.id, 'push')
    
    async def _create_delivery(self, notification_id: str, method: str):
        """Create delivery record."""
        
        delivery = NotificationDelivery(
            notification_id=notification_id,
            delivery_method=method,
            status='pending'
        )
        
        self.db.add(delivery)
        await self.db.commit()
        
        # For in-app notifications, mark as sent immediately
        if method == 'in_app':
            delivery.status = 'sent'
            delivery.sent_at = datetime.utcnow()
            delivery.delivered_at = datetime.utcnow()
            await self.db.commit()
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    async def _send_realtime_notification(self, notification: Notification):
        """Send real-time notification via WebSocket."""
        try:
            # Import here to avoid circular imports
            from app.core.websocket import notification_broadcaster
            
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'category': notification.category,
                'priority': notification.priority,
                'action_url': notification.action_url,
                'action_data': notification.action_data,
                'created_at': notification.created_at.isoformat(),
                'expires_at': notification.expires_at.isoformat() if notification.expires_at else None
            }
            
            await notification_broadcaster.send_notification(notification.user_id, notification_data)
            
        except Exception as e:
            # Don't fail notification creation if WebSocket fails
            import logging
            logging.warning(f"Failed to send real-time notification: {e}")
    
    # Predefined notification methods for common scenarios
    
    async def notify_sync_completed(self, user_id: str, device_name: str, changes_count: int):
        """Notify user about completed sync."""
        return await self.create_notification(
            user_id=user_id,
            title="同步完成",
            message=f"设备 {device_name} 同步完成，处理了 {changes_count} 个变更。",
            notification_type="success",
            category="sync",
            priority="normal",
            expires_hours=24
        )
    
    async def notify_sync_conflict(self, user_id: str, device_name: str, conflicts_count: int):
        """Notify user about sync conflicts."""
        return await self.create_notification(
            user_id=user_id,
            title="同步冲突",
            message=f"设备 {device_name} 同步时发现 {conflicts_count} 个冲突，需要手动解决。",
            notification_type="warning",
            category="sync",
            priority="high",
            action_url="/sync",
            expires_hours=72
        )
    
    async def notify_knowledge_created(self, user_id: str, title: str):
        """Notify user about new knowledge item."""
        return await self.create_notification(
            user_id=user_id,
            title="新知识条目",
            message=f"知识条目 \"{title}\" 已创建。",
            notification_type="info",
            category="knowledge",
            priority="normal",
            expires_hours=48
        )
    
    async def notify_import_completed(self, user_id: str, platform: str, imported_count: int):
        """Notify user about completed import."""
        return await self.create_notification(
            user_id=user_id,
            title="导入完成",
            message=f"从 {platform} 导入完成，成功导入 {imported_count} 个条目。",
            notification_type="success",
            category="import",
            priority="normal",
            expires_hours=48
        )