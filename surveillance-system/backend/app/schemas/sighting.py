"""Sighting schemas for API requests and responses."""

from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SceneAnalysis(BaseModel):
    """Scene analysis schema."""
    crowd_density: Optional[int] = Field(None, ge=0, le=10)
    lighting: Optional[str] = None
    weather_tags: Optional[list] = None


class SightingBase(BaseModel):
    """Base sighting schema."""
    subject_id: Optional[UUID] = None
    camera_id: UUID
    image_id: Optional[UUID] = None
    detection_confidence: float = Field(..., ge=0, le=1)
    recognition_confidence: Optional[float] = Field(None, ge=0, le=1)
    match_distance: Optional[float] = None
    scene_analysis: Optional[SceneAnalysis] = None


class SightingCreate(SightingBase):
    """Schema for creating a sighting."""
    detected_at: datetime


class SightingResponse(SightingBase):
    """Schema for sighting response."""
    sighting_id: UUID
    detected_at: datetime
    processed_at: datetime
    is_recognized: bool
    is_high_confidence: bool
    
    class Config:
        from_attributes = True


class SightingSearch(BaseModel):
    """Schema for sighting search request."""
    subject_id: Optional[UUID] = None
    camera_id: Optional[UUID] = None
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    confidence_min: float = Field(default=0.0, ge=0, le=1)
    limit: int = Field(default=50, ge=1, le=500)
    cursor: Optional[str] = None  # For pagination


class SightingSearchResponse(BaseModel):
    """Schema for sighting search response."""
    sightings: list[SightingResponse]
    next_cursor: Optional[str] = None
    total_count: int
