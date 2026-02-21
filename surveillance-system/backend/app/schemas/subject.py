"""Subject schemas for API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectMetadata(BaseModel):
    """Subject metadata schema."""
    estimated_age: Optional[int] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    department: Optional[str] = None
    clothing_preferences: Optional[List[str]] = None


class SubjectBase(BaseModel):
    """Base subject schema."""
    label: Optional[str] = Field(None, max_length=255)
    subject_type: str = Field(default="unknown")
    status: str = Field(default="active")
    metadata: Optional[SubjectMetadata] = None
    consent_status: str = Field(default="pending")


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""
    label: Optional[str] = Field(None, max_length=255)
    subject_type: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[SubjectMetadata] = None
    consent_status: Optional[str] = None


class SubjectResponse(SubjectBase):
    """Schema for subject response."""
    subject_id: UUID
    enrollment_date: datetime
    last_seen: Optional[datetime]
    retention_until: Optional[datetime]
    image_count: int = 0
    sighting_count: int = 0
    
    class Config:
        from_attributes = True


class SubjectSearch(BaseModel):
    """Schema for subject search request."""
    query: Optional[str] = None
    subject_types: Optional[List[str]] = None
    status: Optional[str] = None
    confidence_min: float = Field(default=0.0, ge=0, le=1)
    seen_after: Optional[datetime] = None
    seen_before: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SubjectEnrollRequest(BaseModel):
    """Schema for enrolling a subject with an image."""
    subject_id: Optional[UUID] = None  # If None, create new subject
    label: Optional[str] = None
    subject_type: Optional[str] = None
    metadata: Optional[SubjectMetadata] = None


class SubjectEnrollResponse(BaseModel):
    """Schema for subject enrollment response."""
    subject_id: UUID
    success: bool
    embedding: Optional[List[float]] = None
    message: str


class FaceSearchRequest(BaseModel):
    """Schema for face search by image."""
    threshold: float = Field(default=0.7, ge=0, le=1)
    max_results: int = Field(default=10, ge=1, le=50)
    camera_filter: Optional[List[UUID]] = None


class FaceSearchResult(BaseModel):
    """Schema for face search result."""
    subject_id: UUID
    label: Optional[str]
    subject_type: str
    similarity: float
    last_seen: Optional[datetime]


class TimelineEvent(BaseModel):
    """Schema for timeline event."""
    sighting_id: UUID
    camera_id: UUID
    camera_name: str
    image_id: Optional[UUID]
    detection_confidence: float
    recognition_confidence: Optional[float]
    detected_at: datetime
    location: Optional[str]


class SubjectTimelineResponse(BaseModel):
    """Schema for subject timeline response."""
    subject_id: UUID
    events: List[TimelineEvent]
    total_count: int
