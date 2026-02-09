"""
WebSocket API Endpoints

Real-time WebSocket endpoints for live notifications and updates.
"""

import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user_id
from app.core.websocket import (
    connection_manager, 
    notification_broadcaster, 
    handle_websocket_message
)
from app.services.notification import NotificationService

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: Optional[str] = Query(None, description="JWT token for authentication")
):
    """WebSocket endpoint for real-time communication."""
    
    # Authenticate user (simplified for WebSocket)
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    try:
        # Verify token (simplified - in production, use proper JWT verification)
        # For now, we'll accept any token and use the user_id from URL
        authenticated_user_id = user_id  # In production, extract from JWT token
        
        # Accept connection
        client_info = {
            'user_agent': websocket.headers.get('user-agent', ''),
            'origin': websocket.headers.get('origin', ''),
        }
        
        await connection_manager.connect(websocket, authenticated_user_id, client_info)
        
        # Send initial data
        async with get_db_session() as db:
            notification_service = NotificationService(db)
            
            # Send unread notification count
            stats = await notification_service.get_notification_stats(authenticated_user_id)
            await connection_manager.send_personal_message({
                'type': 'notification_stats',
                'data': stats,
                'timestamp': None
            }, websocket)
        
        # Listen for messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message
                await handle_websocket_message(websocket, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    'type': 'error',
                    'message': 'Invalid JSON format',
                    'timestamp': None
                }, websocket)
            except Exception as e:
                await connection_manager.send_personal_message({
                    'type': 'error',
                    'message': f'Message handling error: {str(e)}',
                    'timestamp': None
                }, websocket)
                
    except Exception as e:
        await websocket.close(code=4000, reason=f"Connection error: {str(e)}")
    finally:
        connection_manager.disconnect(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        'status': 'active',
        'stats': connection_manager.get_connection_stats(),
        'features': [
            'Real-time notifications',
            'Live sync updates',
            'System messages',
            'Room subscriptions'
        ]
    }


@router.post("/ws/broadcast")
async def broadcast_message(
    message: dict,
    target_users: Optional[list] = None
):
    """Broadcast a message to WebSocket connections (admin only)."""
    # In production, add admin authentication here
    
    if target_users:
        for user_id in target_users:
            await notification_broadcaster.send_system_message(message, [user_id])
    else:
        await notification_broadcaster.send_system_message(message)
    
    return {
        'status': 'sent',
        'target_users': target_users or 'all',
        'message': 'Message broadcasted successfully'
    }


@router.post("/ws/notify/{user_id}")
async def send_websocket_notification(
    user_id: str,
    notification_data: dict
):
    """Send a notification via WebSocket to a specific user."""
    await notification_broadcaster.send_notification(user_id, notification_data)
    
    return {
        'status': 'sent',
        'user_id': user_id,
        'message': 'Notification sent successfully'
    }


@router.post("/ws/sync-update/{user_id}")
async def send_sync_update(
    user_id: str,
    sync_data: dict
):
    """Send a sync update via WebSocket to a specific user."""
    await notification_broadcaster.send_sync_update(user_id, sync_data)
    
    return {
        'status': 'sent',
        'user_id': user_id,
        'message': 'Sync update sent successfully'
    }


@router.get("/ws/connections/{user_id}")
async def get_user_connections(user_id: str):
    """Get connection count for a specific user."""
    return {
        'user_id': user_id,
        'connections': connection_manager.get_user_connections(user_id),
        'is_online': connection_manager.get_user_connections(user_id) > 0
    }