"""Camera schemas for API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class StreamConfig(BaseModel):
    """Stream configuration schema."""
    protocol: str = "rtsp"
    resolution: str = "1920x1080"
    fps: int = 15
    codec: str = "h264"
    auth_type: str = "basic"


class DetectionZone(BaseModel):
    """Detection zone polygon schema."""
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)
    w: float = Field(..., ge=0, le=1)
    h: float = Field(..., ge=0, le=1)


class CameraBase(BaseModel):
    """Base camera schema."""
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    rtsp_url: str = Field(..., min_length=1)
    stream_config: Optional[StreamConfig] = Field(default_factory=StreamConfig)
    detection_zones: Optional[List[DetectionZone]] = None
    is_active: bool = True


class CameraCreate(CameraBase):
    """Schema for creating a camera."""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating a camera."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=500)
    rtsp_url: Optional[str] = None
    stream_config: Optional[StreamConfig] = None
    detection_zones: Optional[List[DetectionZone]] = None
    is_active: Optional[bool] = None


class CameraResponse(CameraBase):
    """Schema for camera response."""
    camera_id: UUID
    health_status: str
    last_frame_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CameraHealth(BaseModel):
    """Camera health status schema."""
    camera_id: UUID
    name: str
    location: Optional[str]
    health_status: str
    is_active: bool
    frame_freshness: str
    detections_last_hour: int
    last_detection_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CameraTestRequest(BaseModel):
    """Schema for testing camera connection."""
    rtsp_url: str
    timeout: int = Field(default=10, ge=1, le=60)


class CameraTestResponse(BaseModel):
    """Schema for camera test result."""
    success: bool
    message: str
    stream_info: Optional[Dict[str, Any]] = None
