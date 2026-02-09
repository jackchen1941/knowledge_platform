"""
Notification API Endpoints

RESTful API endpoints for notification management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import security, get_current_user_id
from app.services.notification import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse,
    NotificationMarkReadRequest,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationFromTemplateRequest,
    BulkNotificationRequest,
    BulkNotificationResponse
)

router = APIRouter()


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.create_notification(
        user_id=user_id,
        **notification_data.dict()
    )
    
    return NotificationResponse.from_orm(notification)


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """List user notifications."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        category=category,
        limit=limit + 1,  # Get one extra to check if there are more
        offset=offset
    )
    
    has_more = len(notifications) > limit
    if has_more:
        notifications = notifications[:limit]
    
    # Get stats for response
    stats = await notification_service.get_notification_stats(user_id)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_orm(n) for n in notifications],
        total=stats['total'],
        unread=stats['unread'],
        has_more=has_more
    )


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Get notification statistics."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    stats = await notification_service.get_notification_stats(user_id)
    
    return NotificationStatsResponse(**stats)


@router.post("/mark-read")
async def mark_notifications_read(
    request: NotificationMarkReadRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Mark notifications as read."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    
    if request.notification_ids:
        # Mark specific notifications as read
        marked_count = 0
        for notification_id in request.notification_ids:
            if await notification_service.mark_as_read(notification_id, user_id):
                marked_count += 1
    else:
        # Mark all notifications as read (optionally filtered by category)
        marked_count = await notification_service.mark_all_as_read(user_id, request.category)
    
    return {"marked": marked_count, "message": f"Marked {marked_count} notifications as read"}


@router.delete("/{notification_id}")
async def archive_notification(
    notification_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Archive (soft delete) a notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    success = await notification_service.archive_notification(notification_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification archived successfully"}


@router.post("/from-template", response_model=NotificationResponse)
async def create_from_template(
    request: NotificationFromTemplateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Create notification from template."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    
    try:
        notification = await notification_service.create_from_template(
            user_id=user_id,
            template_key=request.template_key,
            variables=request.variables,
            priority=request.priority,
            expires_hours=request.expires_hours,
            scheduled_at=request.scheduled_at
        )
        
        return NotificationResponse.from_orm(notification)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/bulk", response_model=BulkNotificationResponse)
async def send_bulk_notifications(
    request: BulkNotificationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send notifications to multiple users."""
    # This endpoint might be restricted to admin users in production
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    
    sent = 0
    failed = 0
    errors = []
    
    for target_user_id in request.user_ids:
        try:
            await notification_service.create_notification(
                user_id=target_user_id,
                title=request.title,
                message=request.message,
                notification_type=request.notification_type,
                category=request.category,
                priority=request.priority,
                expires_hours=request.expires_hours
            )
            sent += 1
        except Exception as e:
            failed += 1
            errors.append(f"Failed to send to user {target_user_id}: {str(e)}")
    
    return BulkNotificationResponse(
        sent=sent,
        failed=failed,
        errors=errors
    )


# Convenience endpoints for common notification types

@router.post("/sync/completed")
async def notify_sync_completed(
    device_name: str,
    changes_count: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send sync completion notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.notify_sync_completed(
        user_id, device_name, changes_count
    )
    
    return NotificationResponse.from_orm(notification)


@router.post("/sync/conflict")
async def notify_sync_conflict(
    device_name: str,
    conflicts_count: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send sync conflict notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.notify_sync_conflict(
        user_id, device_name, conflicts_count
    )
    
    return NotificationResponse.from_orm(notification)


@router.post("/knowledge/created")
async def notify_knowledge_created(
    title: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send knowledge creation notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.notify_knowledge_created(
        user_id, title
    )
    
    return NotificationResponse.from_orm(notification)


@router.post("/import/completed")
async def notify_import_completed(
    platform: str,
    imported_count: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send import completion notification."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.notify_import_completed(
        user_id, platform, imported_count
    )
    
    return NotificationResponse.from_orm(notification)


@router.post("/demo")
async def send_demo_notification(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Send a demo notification for testing WebSocket functionality."""
    user_id = get_current_user_id(credentials)
    
    notification_service = NotificationService(db)
    notification = await notification_service.create_notification(
        user_id=user_id,
        title="WebSocket测试通知",
        message="这是一个测试WebSocket实时推送功能的演示通知。如果您能看到这条消息，说明WebSocket连接正常工作！",
        notification_type="info",
        category="system",
        priority="normal",
        send_realtime=True
    )
    
    return {
        "message": "Demo notification sent successfully",
        "notification_id": notification.id,
        "user_id": user_id,
        "websocket_sent": True
    }