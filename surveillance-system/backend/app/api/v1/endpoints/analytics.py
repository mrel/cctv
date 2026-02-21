"""Analytics and reporting endpoints."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.camera import Camera
from app.models.subject import Subject
from app.models.sighting import Sighting
from app.models.alert import AlertLog
from app.schemas.analytics import (
    HeatmapRequest, HeatmapResponse, HeatmapDataPoint,
    StatisticsResponse, CameraStatsResponse,
    MovementFlowResponse, MovementFlow,
    DemographicsResponse, ExportRequest
)
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get general system statistics."""
    # Camera stats
    camera_result = await db.execute(
        select(func.count(Camera.camera_id))
    )
    total_cameras = camera_result.scalar()
    
    active_camera_result = await db.execute(
        select(func.count(Camera.camera_id))
        .where(Camera.is_active == True)
    )
    active_cameras = active_camera_result.scalar()
    
    # Subject stats
    subject_result = await db.execute(
        select(func.count(Subject.subject_id))
    )
    total_subjects = subject_result.scalar()
    
    known_subjects_result = await db.execute(
        select(func.count(Subject.subject_id))
        .where(Subject.subject_type != "unknown")
    )
    known_subjects = known_subjects_result.scalar()
    
    unknown_subjects_result = await db.execute(
        select(func.count(Subject.subject_id))
        .where(Subject.subject_type == "unknown")
    )
    unknown_subjects = unknown_subjects_result.scalar()
    
    # Sighting stats (24h)
    sightings_24h_result = await db.execute(
        select(func.count(Sighting.sighting_id))
        .where(Sighting.detected_at > func.now() - func.interval("1 day"))
    )
    sightings_24h = sightings_24h_result.scalar()
    
    # Alert stats (24h)
    alerts_24h_result = await db.execute(
        select(func.count(AlertLog.alert_id))
        .where(AlertLog.created_at > func.now() - func.interval("1 day"))
    )
    alerts_24h = alerts_24h_result.scalar()
    
    # Open alerts
    open_alerts_result = await db.execute(
        select(func.count(AlertLog.alert_id))
        .where(AlertLog.status == "open")
    )
    open_alerts = open_alerts_result.scalar()
    
    # Average detections per hour (24h)
    avg_result = await db.execute(
        select(func.count(Sighting.sighting_id) / 24.0)
        .where(Sighting.detected_at > func.now() - func.interval("1 day"))
    )
    avg_per_hour = avg_result.scalar() or 0
    
    return StatisticsResponse(
        total_cameras=total_cameras,
        active_cameras=active_cameras,
        total_subjects=total_subjects,
        known_subjects=known_subjects,
        unknown_subjects=unknown_subjects,
        total_sightings_24h=sightings_24h,
        total_alerts_24h=alerts_24h,
        open_alerts=open_alerts,
        avg_detections_per_hour=round(avg_per_hour, 2)
    )


@router.post("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    request: HeatmapRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get heatmap data for camera activity."""
    time_from = request.time_range[0]
    time_to = request.time_range[1]
    
    # Build query based on granularity
    if request.granularity == "hour":
        time_trunc = "hour"
    elif request.granularity == "day":
        time_trunc = "day"
    else:
        time_trunc = "hour"
    
    query = text(f"""
        SELECT 
            date_trunc(:granularity, s.detected_at) as timestamp,
            s.camera_id,
            c.name as camera_name,
            COUNT(*) as detection_count,
            COUNT(DISTINCT s.subject_id) as unique_subjects
        FROM sightings s
        JOIN cameras c ON s.camera_id = c.camera_id
        WHERE s.camera_id = ANY(:camera_ids)
        AND s.detected_at BETWEEN :time_from AND :time_to
        GROUP BY date_trunc(:granularity, s.detected_at), s.camera_id, c.name
        ORDER BY timestamp, camera_name
    """)
    
    result = await db.execute(query, {
        "granularity": time_trunc,
        "camera_ids": [str(cid) for cid in request.camera_ids],
        "time_from": time_from,
        "time_to": time_to
    })
    
    data = []
    for row in result:
        data.append(HeatmapDataPoint(
            timestamp=row.timestamp,
            camera_id=row.camera_id,
            camera_name=row.camera_name,
            detection_count=row.detection_count,
            unique_subjects=row.unique_subjects
        ))
    
    return HeatmapResponse(
        data=data,
        camera_ids=request.camera_ids,
        time_from=time_from,
        time_to=time_to
    )


@router.get("/cameras/{camera_id}/stats", response_model=CameraStatsResponse)
async def get_camera_stats(
    camera_id: UUID,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for a specific camera."""
    time_from = datetime.utcnow() - timedelta(hours=hours)
    time_to = datetime.utcnow()
    
    # Use the database function
    result = await db.execute(
        text("SELECT * FROM get_camera_stats(:camera_id, :time_from, :time_to)"),
        {
            "camera_id": str(camera_id),
            "time_from": time_from,
            "time_to": time_to
        }
    )
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return CameraStatsResponse(
        camera_id=camera_id,
        total_detections=row.total_detections,
        unique_subjects=row.unique_subjects,
        avg_confidence=round(row.avg_confidence, 3) if row.avg_confidence else 0,
        peak_hour=row.peak_hour,
        peak_count=row.peak_count
    )


@router.get("/movement-flow", response_model=MovementFlowResponse)
async def get_movement_flow(
    time_from: datetime,
    time_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get movement flow between cameras."""
    query = text("""
        WITH subject_movements AS (
            SELECT 
                subject_id,
                camera_id,
                detected_at,
                LAG(camera_id) OVER (PARTITION BY subject_id ORDER BY detected_at) as prev_camera_id,
                LAG(detected_at) OVER (PARTITION BY subject_id ORDER BY detected_at) as prev_detected_at
            FROM sightings
            WHERE detected_at BETWEEN :time_from AND :time_to
            AND subject_id IS NOT NULL
        )
        SELECT 
            sm.prev_camera_id as from_camera_id,
            sm.camera_id as to_camera_id,
            fc.name as from_camera_name,
            tc.name as to_camera_name,
            COUNT(*) as transition_count,
            AVG(EXTRACT(EPOCH FROM (sm.detected_at - sm.prev_detected_at)) / 60) as avg_transition_time_minutes
        FROM subject_movements sm
        JOIN cameras fc ON sm.prev_camera_id = fc.camera_id
        JOIN cameras tc ON sm.camera_id = tc.camera_id
        WHERE sm.prev_camera_id IS NOT NULL
        AND sm.camera_id != sm.prev_camera_id
        GROUP BY sm.prev_camera_id, sm.camera_id, fc.name, tc.name
        ORDER BY transition_count DESC
        LIMIT 50
    """)
    
    result = await db.execute(query, {
        "time_from": time_from,
        "time_to": time_to
    })
    
    flows = []
    for row in result:
        flows.append(MovementFlow(
            from_camera_id=row.from_camera_id,
            to_camera_id=row.to_camera_id,
            from_camera_name=row.from_camera_name,
            to_camera_name=row.to_camera_name,
            transition_count=row.transition_count,
            avg_transition_time_minutes=round(row.avg_transition_time_minutes or 0, 2)
        ))
    
    return MovementFlowResponse(
        flows=flows,
        time_from=time_from,
        time_to=time_to
    )


@router.get("/demographics", response_model=DemographicsResponse)
async def get_demographics(
    time_from: datetime,
    time_to: datetime,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get demographic analytics."""
    # Age distribution
    age_query = text("""
        SELECT 
            CASE 
                WHEN (metadata->>'estimated_age')::int < 18 THEN 'under_18'
                WHEN (metadata->>'estimated_age')::int BETWEEN 18 AND 30 THEN '18_30'
                WHEN (metadata->>'estimated_age')::int BETWEEN 31 AND 45 THEN '31_45'
                WHEN (metadata->>'estimated_age')::int BETWEEN 46 AND 60 THEN '46_60'
                ELSE 'over_60'
            END as age_group,
            COUNT(DISTINCT s.subject_id) as count
        FROM sightings s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE s.detected_at BETWEEN :time_from AND :time_to
        AND sub.metadata->>'estimated_age' IS NOT NULL
        GROUP BY age_group
    """)
    
    age_result = await db.execute(age_query, {
        "time_from": time_from,
        "time_to": time_to
    })
    age_distribution = {row.age_group: row.count for row in age_result}
    
    # Gender distribution
    gender_query = text("""
        SELECT 
            COALESCE(metadata->>'gender', 'unknown') as gender,
            COUNT(DISTINCT s.subject_id) as count
        FROM sightings s
        JOIN subjects sub ON s.subject_id = sub.subject_id
        WHERE s.detected_at BETWEEN :time_from AND :time_to
        GROUP BY metadata->>'gender'
    """)
    
    gender_result = await db.execute(gender_query, {
        "time_from": time_from,
        "time_to": time_to
    })
    gender_distribution = {row.gender: row.count for row in gender_result}
    
    # Repeat visitor frequency
    repeat_query = text("""
        SELECT 
            CASE 
                WHEN visit_count = 1 THEN 'first_time'
                WHEN visit_count BETWEEN 2 AND 5 THEN 'occasional'
                WHEN visit_count BETWEEN 6 AND 20 THEN 'regular'
                ELSE 'frequent'
            END as frequency,
            COUNT(*) as count
        FROM (
            SELECT subject_id, COUNT(*) as visit_count
            FROM sightings
            WHERE detected_at BETWEEN :time_from AND :time_to
            AND subject_id IS NOT NULL
            GROUP BY subject_id
        ) visits
        GROUP BY frequency
    """)
    
    repeat_result = await db.execute(repeat_query, {
        "time_from": time_from,
        "time_to": time_to
    })
    repeat_frequency = {row.frequency: row.count for row in repeat_result}
    
    return DemographicsResponse(
        age_distribution=age_distribution,
        gender_distribution=gender_distribution,
        repeat_visitor_frequency=repeat_frequency,
        time_from=time_from,
        time_to=time_to
    )


@router.post("/export")
async def export_data(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("analytics:read"))
):
    """Export data in specified format."""
    # TODO: Implement data export with async task queue
    return {
        "message": "Export request received",
        "format": request.format,
        "resource_type": request.resource_type,
        "status": "processing"
    }
