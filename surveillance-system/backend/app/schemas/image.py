"""Image schemas for API requests and responses."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates schema."""
    x: int
    y: int
    w: int
    h: int


class FacialLandmarks(BaseModel):
    """Facial landmarks schema."""
    left_eye: Optional[tuple] = None
    right_eye: Optional[tuple] = None
    nose: Optional[tuple] = None
    left_mouth: Optional[tuple] = None
    right_mouth: Optional[tuple] = None


class ImageBase(BaseModel):
    """Base image schema."""
    subject_id: Optional[UUID] = None
    camera_id: Optional[UUID] = None
    image_type: Optional[str] = Field(None, pattern="^(full_frame|face_crop|thumbnail|profile)$")
    bounding_box: Optional[BoundingBox] = None
    landmarks: Optional[Dict[str, Any]] = None


class ImageCreate(ImageBase):
    """Schema for creating an image record."""
    storage_path: str
    storage_bucket: str = "surveillance-images"
    file_size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    resolution: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0, le=1)
    captured_at: datetime


class ImageResponse(ImageBase):
    """Schema for image response."""
    image_id: UUID
    storage_path: str
    storage_bucket: str
    file_size_bytes: Optional[int]
    resolution: Optional[str]
    quality_score: Optional[float]
    captured_at: datetime
    created_at: datetime
    url_available: bool = False
    
    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""
    image_id: UUID
    storage_path: str
    url: Optional[str] = None
    message: str
