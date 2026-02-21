"""Image management endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.minio_client import (
    upload_subject_image, upload_live_frame,
    download_image, get_presigned_url
)
from app.models.image import Image
from app.schemas.image import ImageCreate, ImageResponse, ImageUploadResponse
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get image metadata by ID."""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return ImageResponse.from_orm(image)


@router.get("/{image_id}/download")
async def download_image_file(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Download image file by ID."""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Extract bucket and object name from storage path
    parts = image.storage_path.split("/", 1)
    bucket = parts[0]
    object_name = parts[1] if len(parts) > 1 else ""
    
    try:
        image_data = await download_image(bucket, object_name)
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"attachment; filename={image_id}.jpg"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download image: {str(e)}"
        )


@router.get("/{image_id}/url")
async def get_image_url(
    image_id: UUID,
    expires: int = 3600,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get presigned URL for image access."""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    parts = image.storage_path.split("/", 1)
    bucket = parts[0]
    object_name = parts[1] if len(parts) > 1 else ""
    
    try:
        url = await get_presigned_url(bucket, object_name, expires)
        return {"url": url, "expires_in": expires}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate URL: {str(e)}"
        )


@router.post("/upload/subject/{subject_id}", response_model=ImageUploadResponse)
async def upload_subject_image_endpoint(
    subject_id: UUID,
    image: UploadFile = File(...),
    image_type: str = "gallery",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Upload image for a subject."""
    # Read image data
    image_data = await image.read()
    
    # Upload to MinIO
    image_id = str(uuid4())
    storage_path = await upload_subject_image(
        str(subject_id),
        image_id,
        image_data,
        image_type
    )
    
    # Create image record
    db_image = Image(
        image_id=image_id,
        subject_id=subject_id,
        storage_path=storage_path,
        storage_bucket="surveillance-subjects",
        image_type=image_type,
        file_size_bytes=len(image_data),
        captured_at=datetime.utcnow()
    )
    
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    
    return ImageUploadResponse(
        image_id=db_image.image_id,
        storage_path=storage_path,
        message="Image uploaded successfully"
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("subjects:write"))
):
    """Delete image by ID."""
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete from MinIO
    parts = image.storage_path.split("/", 1)
    bucket = parts[0]
    object_name = parts[1] if len(parts) > 1 else ""
    
    from app.core.minio_client import delete_object
    await delete_object(bucket, object_name)
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return None
