"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Set, Dict
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPBearer

from app.core.redis import get_redis, publish, subscribe
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter()
security = HTTPBearer()

# Store active WebSocket connections
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "alerts": set(),
            "detections": set(),
            "cameras": set(),
            "system": set()
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and store connection."""
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].add(websocket)
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove connection."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
    
    async def broadcast(self, message: dict, channel: str):
        """Broadcast message to all connections in channel."""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections[channel].discard(conn)


manager = ConnectionManager()


@router.websocket("/alerts")
async def alerts_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """WebSocket for real-time alert notifications."""
    # TODO: Validate token
    await manager.connect(websocket, "alerts")
    
    try:
        # Subscribe to Redis channel
        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe("alerts:updates")
        
        while True:
            # Check for Redis messages
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
            
            # Check for client ping
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1
                )
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
        await pubsub.unsubscribe("alerts:updates")


@router.websocket("/detections")
async def detections_websocket(
    websocket: WebSocket,
    camera_id: UUID = Query(None),
    token: str = Query(...)
):
    """WebSocket for real-time detection updates."""
    await manager.connect(websocket, "detections")
    
    try:
        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe("detections:updates")
        
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                data = json.loads(message["data"])
                
                # Filter by camera if specified
                if camera_id and data.get("camera_id") != str(camera_id):
                    continue
                
                await websocket.send_json(data)
            
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1
                )
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "detections")
        await pubsub.unsubscribe("detections:updates")


@router.websocket("/cameras/{camera_id}/stream")
async def camera_stream_websocket(
    websocket: WebSocket,
    camera_id: UUID,
    token: str = Query(...)
):
    """WebSocket for camera stream proxy (HLS/WebRTC signaling)."""
    await manager.connect(websocket, "cameras")
    
    try:
        while True:
            # Receive signaling messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "offer":
                # TODO: Forward to WebRTC gateway
                pass
            elif message.get("type") == "ice-candidate":
                # TODO: Forward ICE candidate
                pass
            
            # Echo back for now
            await websocket.send_json({
                "type": "ack",
                "camera_id": str(camera_id)
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "cameras")


@router.websocket("/system")
async def system_websocket(
    websocket: WebSocket,
    token: str = Query(...)
):
    """WebSocket for system health and status updates."""
    await manager.connect(websocket, "system")
    
    try:
        while True:
            # Send periodic health updates
            await websocket.send_json({
                "type": "health",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy"
            })
            
            # Wait for next update interval
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "system")


# Helper function to broadcast messages
async def broadcast_alert(alert_data: dict):
    """Broadcast alert to all connected clients."""
    await manager.broadcast({
        "type": "alert",
        "data": alert_data
    }, "alerts")


async def broadcast_detection(detection_data: dict):
    """Broadcast detection to all connected clients."""
    await manager.broadcast({
        "type": "detection",
        "data": detection_data
    }, "detections")
