"""Analytics schemas for API requests and responses."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HeatmapRequest(BaseModel):
    """Schema for heatmap analytics request."""
    camera_ids: List[UUID]
    time_range: List[datetime]
    granularity: str = Field(default="hour", pattern="^(minute|hour|day|week)$")


class HeatmapDataPoint(BaseModel):
    """Schema for heatmap data point."""
    timestamp: datetime
    camera_id: UUID
    camera_name: str
    detection_count: int
    unique_subjects: int


class HeatmapResponse(BaseModel):
    """Schema for heatmap response."""
    data: List[HeatmapDataPoint]
    camera_ids: List[UUID]
    time_from: datetime
    time_to: datetime


class TimelineResponse(BaseModel):
    """Schema for subject timeline response."""
    subject_id: UUID
    events: List[Dict[str, Any]]
    total_count: int
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]


class StatisticsResponse(BaseModel):
    """Schema for general statistics response."""
    total_cameras: int
    active_cameras: int
    total_subjects: int
    known_subjects: int
    unknown_subjects: int
    total_sightings_24h: int
    total_alerts_24h: int
    open_alerts: int
    avg_detections_per_hour: float


class CameraStatsRequest(BaseModel):
    """Schema for camera statistics request."""
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None


class CameraStatsResponse(BaseModel):
    """Schema for camera statistics response."""
    camera_id: UUID
    total_detections: int
    unique_subjects: int
    avg_confidence: float
    peak_hour: Optional[int]
    peak_count: int


class MovementFlow(BaseModel):
    """Schema for movement flow between cameras."""
    from_camera_id: UUID
    to_camera_id: UUID
    from_camera_name: str
    to_camera_name: str
    transition_count: int
    avg_transition_time_minutes: float


class MovementFlowResponse(BaseModel):
    """Schema for movement flow response."""
    flows: List[MovementFlow]
    time_from: datetime
    time_to: datetime


class DemographicsResponse(BaseModel):
    """Schema for demographics analytics response."""
    age_distribution: Dict[str, int]
    gender_distribution: Dict[str, int]
    repeat_visitor_frequency: Dict[str, int]
    time_from: datetime
    time_to: datetime


class ExportRequest(BaseModel):
    """Schema for data export request."""
    format: str = Field(default="csv", pattern="^(csv|json|pdf)$")
    resource_type: str = Field(..., pattern="^(sightings|subjects|alerts|audit)$")
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
