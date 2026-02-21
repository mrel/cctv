"""Camera model for surveillance camera configuration."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Camera(Base):
    """Camera configuration and metadata."""
    
    __tablename__ = "cameras"
    
    camera_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    rtsp_url = Column(String(1000), nullable=False)
    stream_config = Column(JSON, default={
        "protocol": "rtsp",
        "resolution": "1920x1080",
        "fps": 15,
        "codec": "h264",
        "auth_type": "basic"
    })
    detection_zones = Column(JSON)  # Polygon coordinates for ROI
    is_active = Column(Boolean, default=True)
    health_status = Column(String(50), default="unknown")
    last_frame_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sightings = relationship("Sighting", back_populates="camera")
    images = relationship("Image", back_populates="camera")
    alert_logs = relationship("AlertLog", back_populates="camera")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "camera_id": str(self.camera_id),
            "name": self.name,
            "location": self.location,
            "rtsp_url": self.rtsp_url,
            "stream_config": self.stream_config,
            "detection_zones": self.detection_zones,
            "is_active": self.is_active,
            "health_status": self.health_status,
            "last_frame_at": self.last_frame_at.isoformat() if self.last_frame_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_health(self, status: str) -> None:
        """Update camera health status."""
        self.health_status = status
        if status == "healthy":
            self.last_frame_at = datetime.utcnow()
