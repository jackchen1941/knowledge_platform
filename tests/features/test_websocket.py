#!/usr/bin/env python3
"""
WebSocket Test Script

Test WebSocket functionality directly.
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    """Test WebSocket connection and messaging."""
    
    # WebSocket URL
    ws_url = "ws://localhost:8000/api/v1/ws/test-user-123?token=test-token"
    
    try:
        print(f"🔗 Connecting to WebSocket: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send ping message
            ping_message = {
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent ping: {ping_message}")
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 Received: {response_data}")
            
            # Subscribe to notifications room
            subscribe_message = {
                "type": "subscribe",
                "room": "notifications"
            }
            
            await websocket.send(json.dumps(subscribe_message))
            print(f"📤 Sent subscribe: {subscribe_message}")
            
            # Wait for subscription confirmation
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 Received: {response_data}")
            
            # Get connection stats
            stats_message = {
                "type": "get_stats"
            }
            
            await websocket.send(json.dumps(stats_message))
            print(f"📤 Sent get_stats: {stats_message}")
            
            # Wait for stats response
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 Received stats: {response_data}")
            
            print("✅ WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())