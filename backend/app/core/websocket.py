"""
WebSocket Manager

Real-time WebSocket connection management for live notifications and updates.
"""

import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        # Active connections: user_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata: websocket -> user info
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        # Room subscriptions: room_name -> set of websockets
        self.rooms: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, client_info: Optional[Dict[str, Any]] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow(),
            'client_info': client_info or {},
            'subscriptions': set()
        }
        
        logger.info(f"WebSocket connected: user_id={user_id}, total_connections={self.get_total_connections()}")
        
        # Send welcome message
        await self.send_personal_message({
            'type': 'connection_established',
            'message': 'WebSocket connection established',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.connection_info:
            user_id = self.connection_info[websocket]['user_id']
            subscriptions = self.connection_info[websocket]['subscriptions']
            
            # Remove from user connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from rooms
            for room in subscriptions:
                if room in self.rooms:
                    self.rooms[room].discard(websocket)
                    if not self.rooms[room]:
                        del self.rooms[room]
            
            # Remove connection info
            del self.connection_info[websocket]
            
            logger.info(f"WebSocket disconnected: user_id={user_id}, total_connections={self.get_total_connections()}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Failed to send message to websocket: {e}")
            self.disconnect(websocket)
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id].copy():
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket)
    
    async def send_to_room(self, message: Dict[str, Any], room: str):
        """Send a message to all connections in a room."""
        if room in self.rooms:
            disconnected = []
            for websocket in self.rooms[room].copy():
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                except Exception as e:
                    logger.error(f"Failed to send message to room {room}: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for websocket in list(self.connection_info.keys()):
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def subscribe_to_room(self, websocket: WebSocket, room: str):
        """Subscribe a WebSocket to a room."""
        if websocket in self.connection_info:
            # Add to room
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(websocket)
            
            # Update connection info
            self.connection_info[websocket]['subscriptions'].add(room)
            
            logger.info(f"WebSocket subscribed to room: {room}")
            
            # Send confirmation
            await self.send_personal_message({
                'type': 'room_subscribed',
                'room': room,
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
    
    async def unsubscribe_from_room(self, websocket: WebSocket, room: str):
        """Unsubscribe a WebSocket from a room."""
        if websocket in self.connection_info:
            # Remove from room
            if room in self.rooms:
                self.rooms[room].discard(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]
            
            # Update connection info
            self.connection_info[websocket]['subscriptions'].discard(room)
            
            logger.info(f"WebSocket unsubscribed from room: {room}")
            
            # Send confirmation
            await self.send_personal_message({
                'type': 'room_unsubscribed',
                'room': room,
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
    
    def get_user_connections(self, user_id: str) -> int:
        """Get number of active connections for a user."""
        return len(self.active_connections.get(user_id, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return len(self.connection_info)
    
    def get_room_connections(self, room: str) -> int:
        """Get number of connections in a room."""
        return len(self.rooms.get(room, set()))
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            'total_connections': self.get_total_connections(),
            'total_users': len(self.active_connections),
            'total_rooms': len(self.rooms),
            'rooms': {room: len(connections) for room, connections in self.rooms.items()},
            'users': {user_id: len(connections) for user_id, connections in self.active_connections.items()}
        }


class NotificationBroadcaster:
    """Handles broadcasting notifications via WebSocket."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def send_notification(self, user_id: str, notification_data: Dict[str, Any]):
        """Send a notification to a specific user."""
        message = {
            'type': 'notification',
            'data': notification_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.connection_manager.send_to_user(message, user_id)
    
    async def send_sync_update(self, user_id: str, sync_data: Dict[str, Any]):
        """Send a sync update to a specific user."""
        message = {
            'type': 'sync_update',
            'data': sync_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.connection_manager.send_to_user(message, user_id)
    
    async def send_knowledge_update(self, user_id: str, knowledge_data: Dict[str, Any]):
        """Send a knowledge update to a specific user."""
        message = {
            'type': 'knowledge_update',
            'data': knowledge_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.connection_manager.send_to_user(message, user_id)
    
    async def send_system_message(self, message_data: Dict[str, Any], target_users: Optional[List[str]] = None):
        """Send a system message to specific users or broadcast to all."""
        message = {
            'type': 'system_message',
            'data': message_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if target_users:
            for user_id in target_users:
                await self.connection_manager.send_to_user(message, user_id)
        else:
            await self.connection_manager.broadcast(message)


# Global connection manager instance
connection_manager = ConnectionManager()
notification_broadcaster = NotificationBroadcaster(connection_manager)


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming WebSocket messages."""
    message_type = message.get('type')
    
    if message_type == 'ping':
        # Respond to ping with pong
        await connection_manager.send_personal_message({
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    
    elif message_type == 'subscribe':
        # Subscribe to a room
        room = message.get('room')
        if room:
            await connection_manager.subscribe_to_room(websocket, room)
    
    elif message_type == 'unsubscribe':
        # Unsubscribe from a room
        room = message.get('room')
        if room:
            await connection_manager.unsubscribe_from_room(websocket, room)
    
    elif message_type == 'get_stats':
        # Send connection statistics
        stats = connection_manager.get_connection_stats()
        await connection_manager.send_personal_message({
            'type': 'stats',
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    
    else:
        # Unknown message type
        await connection_manager.send_personal_message({
            'type': 'error',
            'message': f'Unknown message type: {message_type}',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)