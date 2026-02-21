"""Image model for storing image metadata and storage paths."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Image(Base):
    """Image asset registry with metadata."""
    
    __tablename__ = "images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id", ondelete="SET NULL"))
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.camera_id", ondelete="SET NULL"))
    storage_path = Column(String(500), nullable=False)
    storage_bucket = Column(String(100), default="surveillance-images")
    image_type = Column(String(50))  # full_frame, face_crop, thumbnail, profile
    file_size_bytes = Column(Integer)
    checksum = Column(String(64))  # SHA-256
    resolution = Column(String(20))
    quality_score = Column(Float)
    bounding_box = Column(JSON)  # {"x": 120, "y": 340, "w": 100, "h": 120}
    landmarks = Column(JSON)  # Facial keypoints
    captured_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="images")
    camera = relationship("Camera", back_populates="images")
    sightings = relationship("Sighting", back_populates="image")
    
    def to_dict(self, include_url: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = {
            "image_id": str(self.image_id),
            "subject_id": str(self.subject_id) if self.subject_id else None,
            "camera_id": str(self.camera_id) if self.camera_id else None,
            "storage_path": self.storage_path,
            "storage_bucket": self.storage_bucket,
            "image_type": self.image_type,
            "file_size_bytes": self.file_size_bytes,
            "resolution": self.resolution,
            "quality_score": self.quality_score,
            "bounding_box": self.bounding_box,
            "landmarks": self.landmarks,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_url:
            # Generate presigned URL (async, so just indicate it's available)
            data["url_available"] = True
        
        return data
    
    @property
    def minio_bucket(self) -> str:
        """Extract bucket name from storage path."""
        return self.storage_path.split("/")[0] if "/" in self.storage_path else self.storage_bucket
    
    @property
    def minio_object(self) -> str:
        """Extract object name from storage path."""
        parts = self.storage_path.split("/", 1)
        return parts[1] if len(parts) > 1 else ""
