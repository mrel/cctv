"""Sighting endpoints."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.sighting import Sighting
from app.models.camera import Camera
from app.models.subject import Subject
from app.schemas.sighting import SightingCreate, SightingResponse, SightingSearch, SightingSearchResponse
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("/search", response_model=SightingSearchResponse)
async def search_sightings(
    subject_id: Optional[UUID] = None,
    camera_id: Optional[UUID] = None,
    time_from: Optional[datetime] = None,
    time_to: Optional[datetime] = None,
    confidence_min: float = Query(0.0, ge=0, le=1),
    limit: int = Query(50, ge=1, le=500),
    cursor: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search sightings with filters."""
    query = select(Sighting)
    
    if subject_id:
        query = query.where(Sighting.subject_id == subject_id)
    
    if camera_id:
        query = query.where(Sighting.camera_id == camera_id)
    
    if time_from:
        query = query.where(Sighting.detected_at >= time_from)
    
    if time_to:
        query = query.where(Sighting.detected_at <= time_to)
    
    if confidence_min > 0:
        query = query.where(Sighting.detection_confidence >= confidence_min)
    
    # Cursor-based pagination
    if cursor:
        try:
            cursor_time = datetime.fromisoformat(cursor)
            query = query.where(Sighting.detected_at < cursor_time)
        except ValueError:
            pass
    
    query = query.order_by(desc(Sighting.detected_at)).limit(limit + 1)
    
    result = await db.execute(query)
    sightings = result.scalars().all()
    
    # Check if there are more results
    has_more = len(sightings) > limit
    sightings = list(sightings)[:limit]
    
    # Generate next cursor
    next_cursor = None
    if has_more and sightings:
        next_cursor = sightings[-1].detected_at.isoformat()
    
    return SightingSearchResponse(
        sightings=[SightingResponse.from_orm(s) for s in sightings],
        next_cursor=next_cursor,
        total_count=len(sightings)
    )


@router.get("/{sighting_id}", response_model=SightingResponse)
async def get_sighting(
    sighting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sighting by ID."""
    result = await db.execute(
        select(Sighting).where(Sighting.sighting_id == sighting_id)
    )
    sighting = result.scalar_one_or_none()
    
    if not sighting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sighting not found"
        )
    
    return SightingResponse.from_orm(sighting)


@router.post("", response_model=SightingResponse, status_code=status.HTTP_201_CREATED)
async def create_sighting(
    sighting: SightingCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("sightings:write"))
):
    """Create a new sighting (typically called by recognition service)."""
    db_sighting = Sighting(
        subject_id=sighting.subject_id,
        camera_id=sighting.camera_id,
        image_id=sighting.image_id,
        detection_confidence=sighting.detection_confidence,
        recognition_confidence=sighting.recognition_confidence,
        match_distance=sighting.match_distance,
        scene_analysis=sighting.scene_analysis.dict() if sighting.scene_analysis else None,
        detected_at=sighting.detected_at
    )
    
    db.add(db_sighting)
    await db.commit()
    await db.refresh(db_sighting)
    
    return SightingResponse.from_orm(db_sighting)


@router.get("/recent", response_model=List[SightingResponse])
async def get_recent_sightings(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent sightings."""
    result = await db.execute(
        select(Sighting)
        .order_by(desc(Sighting.detected_at))
        .limit(limit)
    )
    sightings = result.scalars().all()
    
    return [SightingResponse.from_orm(s) for s in sightings]
