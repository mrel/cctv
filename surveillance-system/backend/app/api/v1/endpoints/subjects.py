"""Subject management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy import select, desc, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.minio_client import upload_subject_image, get_subject_image_url
from app.core.redis import cache_get, cache_set, cache_delete_pattern
from app.models.subject import Subject
from app.models.image import Image
from app.models.sighting import Sighting
from app.schemas.subject import (
    SubjectCreate, SubjectUpdate, SubjectResponse, SubjectSearch,
    SubjectEnrollRequest, SubjectEnrollResponse,
    FaceSearchRequest, FaceSearchResult, SubjectTimelineResponse, TimelineEvent
)
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_type: Optional[str] = None,
    status: Optional[str] = None,
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all subjects with optional filtering."""
    # Build query
    q = select(Subject)
    
    if subject_type:
        q = q.where(Subject.subject_type == subject_type)
    
    if status:
        q = q.where(Subject.status == status)
    
    if query:
        q = q.where(Subject.label.ilike(f"%{query}%"))
    
    q = q.order_by(desc(Subject.last_seen)).offset(skip).limit(limit)
    
    result = await db.execute(q)
    subjects = result.scalars().all()
    
    return [SubjectResponse.from_orm(s) for s in subjects]


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Create a new subject."""
    db_subject = Subject(
        label=subject.label,
        subject_type=subject.subject_type,
        status=subject.status,
        metadata=subject.metadata.dict() if subject.metadata else None,
        consent_status=subject.consent_status
    )
    
    db.add(db_subject)
    await db.commit()
    await db.refresh(db_subject)
    
    return SubjectResponse.from_orm(db_subject)


@router.get("/search", response_model=List[SubjectResponse])
async def search_subjects(
    search: SubjectSearch = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search subjects with filters."""
    q = select(Subject)
    
    if search.query:
        q = q.where(Subject.label.ilike(f"%{search.query}%"))
    
    if search.subject_types:
        q = q.where(Subject.subject_type.in_(search.subject_types))
    
    if search.status:
        q = q.where(Subject.status == search.status)
    
    if search.seen_after:
        q = q.where(Subject.last_seen >= search.seen_after)
    
    if search.seen_before:
        q = q.where(Subject.last_seen <= search.seen_before)
    
    q = q.order_by(desc(Subject.last_seen)).offset(search.offset).limit(search.limit)
    
    result = await db.execute(q)
    subjects = result.scalars().all()
    
    return [SubjectResponse.from_orm(s) for s in subjects]


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get subject by ID."""
    cache_key = f"subject:{subject_id}"
    cached = await cache_get(cache_key)
    if cached:
        return SubjectResponse(**cached)
    
    result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    response = SubjectResponse.from_orm(subject)
    await cache_set(cache_key, response.dict(), expire=300)
    
    return response


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID,
    subject_update: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Update subject by ID."""
    result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    update_data = subject_update.dict(exclude_unset=True)
    
    if "metadata" in update_data and update_data["metadata"]:
        update_data["metadata"] = update_data["metadata"].dict()
    
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    await db.commit()
    await db.refresh(subject)
    
    # Invalidate cache
    await cache_delete_pattern(f"subject:{subject_id}")
    
    return SubjectResponse.from_orm(subject)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Delete subject by ID (GDPR deletion)."""
    result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    await db.delete(subject)
    await db.commit()
    
    # Invalidate cache
    await cache_delete_pattern(f"subject:{subject_id}")
    
    return None


@router.get("/{subject_id}/timeline", response_model=SubjectTimelineResponse)
async def get_subject_timeline(
    subject_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get subject movement timeline."""
    # Use the database function for timeline
    result = await db.execute(
        text("SELECT * FROM get_subject_timeline(:subject_id, NULL, NULL, :limit)"),
        {"subject_id": str(subject_id), "limit": limit}
    )
    
    events = []
    for row in result:
        events.append(TimelineEvent(
            sighting_id=row.sighting_id,
            camera_id=row.camera_id,
            camera_name=row.camera_name,
            image_id=row.image_id,
            detection_confidence=row.detection_confidence,
            recognition_confidence=row.recognition_confidence,
            detected_at=row.detected_at,
            location=row.location
        ))
    
    return SubjectTimelineResponse(
        subject_id=subject_id,
        events=events,
        total_count=len(events)
    )


@router.post("/{subject_id}/enroll", response_model=SubjectEnrollResponse)
async def enroll_subject(
    subject_id: UUID,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Enroll subject with reference image."""
    result = await db.execute(
        select(Subject).where(Subject.subject_id == subject_id)
    )
    subject = result.scalar_one_or_none()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # TODO: Process image with recognition service to generate embedding
    # For now, return success
    
    return SubjectEnrollResponse(
        subject_id=subject_id,
        success=True,
        message="Subject enrolled successfully"
    )


@router.post("/search-by-image", response_model=List[FaceSearchResult])
async def search_by_image(
    image: UploadFile = File(...),
    threshold: float = Query(0.7, ge=0, le=1),
    max_results: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search subjects by uploading a face image."""
    # TODO: Process image with recognition service
    # For now, return empty results
    return []


@router.post("/vector-search", response_model=List[FaceSearchResult])
async def vector_search(
    embedding: List[float],
    threshold: float = Query(0.7, ge=0, le=1),
    max_results: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search subjects by face embedding vector."""
    # Use the database function for vector search
    result = await db.execute(
        text("SELECT * FROM search_subjects_by_face(:embedding, :threshold, :max_results)"),
        {
            "embedding": embedding,
            "threshold": threshold,
            "max_results": max_results
        }
    )
    
    results = []
    for row in result:
        results.append(FaceSearchResult(
            subject_id=row.subject_id,
            label=row.label,
            subject_type=row.subject_type,
            similarity=row.similarity,
            last_seen=row.last_seen
        ))
    
    return results
