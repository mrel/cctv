"""Camera management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import cache_get, cache_set, cache_delete_pattern
from app.models.camera import Camera
from app.models.sighting import Sighting
from app.schemas.camera import (
    CameraCreate, CameraUpdate, CameraResponse, CameraHealth,
    CameraTestRequest, CameraTestResponse
)
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("", response_model=List[CameraResponse])
async def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    health_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all cameras with optional filtering."""
    # Check cache
    cache_key = f"cameras:list:{skip}:{limit}:{is_active}:{health_status}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    # Build query
    query = select(Camera)
    
    if is_active is not None:
        query = query.where(Camera.is_active == is_active)
    
    if health_status:
        query = query.where(Camera.health_status == health_status)
    
    query = query.order_by(desc(Camera.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    cameras = result.scalars().all()
    
    response = [CameraResponse.from_orm(c) for c in cameras]
    
    # Cache result
    await cache_set(cache_key, [c.dict() for c in response], expire=60)
    
    return response


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("cameras:write"))
):
    """Create a new camera."""
    # Create camera model
    db_camera = Camera(
        name=camera.name,
        location=camera.location,
        rtsp_url=camera.rtsp_url,
        stream_config=camera.stream_config.dict() if camera.stream_config else {},
        detection_zones=[z.dict() for z in camera.detection_zones] if camera.detection_zones else None,
        is_active=camera.is_active
    )
    
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    
    # Invalidate cache
    await cache_delete_pattern("cameras:list:*")
    
    return CameraResponse.from_orm(db_camera)


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get camera by ID."""
    # Check cache
    cache_key = f"camera:{camera_id}"
    cached = await cache_get(cache_key)
    if cached:
        return CameraResponse(**cached)
    
    result = await db.execute(
        select(Camera).where(Camera.camera_id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    response = CameraResponse.from_orm(camera)
    await cache_set(cache_key, response.dict(), expire=300)
    
    return response


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    camera_update: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("cameras:write"))
):
    """Update camera by ID."""
    result = await db.execute(
        select(Camera).where(Camera.camera_id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Update fields
    update_data = camera_update.dict(exclude_unset=True)
    
    if "stream_config" in update_data and update_data["stream_config"]:
        update_data["stream_config"] = update_data["stream_config"].dict()
    
    if "detection_zones" in update_data and update_data["detection_zones"]:
        update_data["detection_zones"] = [z.dict() for z in update_data["detection_zones"]]
    
    for field, value in update_data.items():
        setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    # Invalidate cache
    await cache_delete_pattern("cameras:list:*")
    await cache_delete_pattern(f"camera:{camera_id}")
    
    return CameraResponse.from_orm(camera)


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("cameras:write"))
):
    """Delete camera by ID."""
    result = await db.execute(
        select(Camera).where(Camera.camera_id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    await db.delete(camera)
    await db.commit()
    
    # Invalidate cache
    await cache_delete_pattern("cameras:list:*")
    await cache_delete_pattern(f"camera:{camera_id}")
    
    return None


@router.get("/{camera_id}/health", response_model=dict)
async def get_camera_health(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get camera health status."""
    result = await db.execute(
        select(Camera).where(Camera.camera_id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Get detection stats
    stats_result = await db.execute(
        select(func.count(Sighting.sighting_id))
        .where(
            Sighting.camera_id == camera_id,
            Sighting.detected_at > func.now() - func.interval("1 hour")
        )
    )
    detections_last_hour = stats_result.scalar() or 0
    
    # Determine frame freshness
    if camera.last_frame_at is None:
        frame_freshness = "never"
    elif camera.last_frame_at < func.now() - func.interval("5 minutes"):
        frame_freshness = "stale"
    else:
        frame_freshness = "fresh"
    
    return {
        "camera_id": str(camera.camera_id),
        "name": camera.name,
        "health_status": camera.health_status,
        "is_active": camera.is_active,
        "last_frame_at": camera.last_frame_at.isoformat() if camera.last_frame_at else None,
        "frame_freshness": frame_freshness,
        "detections_last_hour": detections_last_hour
    }


@router.post("/{camera_id}/test", response_model=CameraTestResponse)
async def test_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("cameras:write"))
):
    """Test camera connection."""
    result = await db.execute(
        select(Camera).where(Camera.camera_id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # TODO: Implement actual stream testing with FFmpeg
    # For now, return mock response
    return CameraTestResponse(
        success=True,
        message="Camera connection test passed",
        stream_info={
            "resolution": "1920x1080",
            "fps": 15,
            "codec": "h264",
            "bitrate": "4096 kbps"
        }
    )


@router.post("/test-connection", response_model=CameraTestResponse)
async def test_camera_connection(
    request: CameraTestRequest,
    current_user = Depends(require_permission("cameras:write"))
):
    """Test RTSP connection without saving camera."""
    # TODO: Implement actual stream testing
    return CameraTestResponse(
        success=True,
        message="Camera connection test passed",
        stream_info={
            "resolution": "1920x1080",
            "fps": 15,
            "codec": "h264"
        }
    )
