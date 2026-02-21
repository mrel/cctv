"""Sighting model for face detection events."""

from datetime import datetime
from uuid import uuid4
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sighting(Base):
    """Face detection and recognition event."""
    
    __tablename__ = "sightings"
    
    sighting_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.subject_id", ondelete="SET NULL"))
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.camera_id", ondelete="SET NULL"))
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.image_id", ondelete="SET NULL"))
    detection_confidence = Column(Float, nullable=False)
    recognition_confidence = Column(Float)
    match_distance = Column(Float)  # Vector distance metric
    scene_analysis = Column(JSON)  # crowd_density, lighting, weather_tags
    detected_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="sightings")
    camera = relationship("Camera", back_populates="sightings")
    image = relationship("Image", back_populates="sightings")
    alert_logs = relationship("AlertLog", back_populates="sighting")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "sighting_id": str(self.sighting_id),
            "subject_id": str(self.subject_id) if self.subject_id else None,
            "camera_id": str(self.camera_id) if self.camera_id else None,
            "image_id": str(self.image_id) if self.image_id else None,
            "detection_confidence": self.detection_confidence,
            "recognition_confidence": self.recognition_confidence,
            "match_distance": self.match_distance,
            "scene_analysis": self.scene_analysis,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
    
    @property
    def is_recognized(self) -> bool:
        """Check if subject was recognized."""
        return self.subject_id is not None and self.recognition_confidence is not None
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if detection has high confidence."""
        return self.detection_confidence >= 0.8
