"""
MinIO client for object storage operations.
Handles image storage, retrieval, and lifecycle management.
"""

import io
from typing import Optional, BinaryIO
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Global MinIO client
minio_client: Optional[Minio] = None


def get_minio_client() -> Minio:
    """Get MinIO client instance."""
    if minio_client is None:
        raise RuntimeError("MinIO client not initialized")
    return minio_client


async def init_minio() -> None:
    """Initialize MinIO connection."""
    global minio_client
    logger.info("Initializing MinIO connection...")
    
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # Test connection and create buckets if needed
        for bucket in [
            settings.MINIO_BUCKET_LIVE,
            settings.MINIO_BUCKET_SUBJECTS,
            settings.MINIO_BUCKET_ARCHIVE,
            settings.MINIO_BUCKET_TEMP
        ]:
            if not minio_client.bucket_exists(bucket):
                minio_client.make_bucket(bucket)
                logger.info(f"Created bucket: {bucket}")
        
        logger.info("MinIO connection established")
        
    except Exception as e:
        logger.error("Failed to initialize MinIO", error=str(e))
        raise


async def close_minio() -> None:
    """Close MinIO connection (no-op for MinIO client)."""
    global minio_client
    logger.info("Closing MinIO connection...")
    minio_client = None
    logger.info("MinIO connection closed")


# Object operations
async def upload_image(
    bucket: str,
    object_name: str,
    data: bytes,
    content_type: str = "image/jpeg",
    metadata: Optional[dict] = None
) -> str:
    """
    Upload image to MinIO.
    Returns the object path.
    """
    client = get_minio_client()
    
    try:
        # Convert bytes to stream
        data_stream = io.BytesIO(data)
        
        # Upload object
        client.put_object(
            bucket,
            object_name,
            data_stream,
            length=len(data),
            content_type=content_type,
            metadata=metadata or {}
        )
        
        logger.debug(
            "Image uploaded",
            bucket=bucket,
            object=object_name,
            size=len(data)
        )
        
        return f"{bucket}/{object_name}"
        
    except S3Error as e:
        logger.error(
            "Failed to upload image",
            bucket=bucket,
            object=object_name,
            error=str(e)
        )
        raise


async def download_image(bucket: str, object_name: str) -> bytes:
    """Download image from MinIO."""
    client = get_minio_client()
    
    try:
        response = client.get_object(bucket, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        
        return data
        
    except S3Error as e:
        logger.error(
            "Failed to download image",
            bucket=bucket,
            object=object_name,
            error=str(e)
        )
        raise


async def get_presigned_url(
    bucket: str,
    object_name: str,
    expires: int = 3600
) -> str:
    """
    Generate presigned URL for temporary access.
    Default expiration: 1 hour.
    """
    client = get_minio_client()
    
    try:
        url = client.presigned_get_object(
            bucket,
            object_name,
            expires=timedelta(seconds=expires)
        )
        return url
        
    except S3Error as e:
        logger.error(
            "Failed to generate presigned URL",
            bucket=bucket,
            object=object_name,
            error=str(e)
        )
        raise


async def delete_object(bucket: str, object_name: str) -> bool:
    """Delete object from MinIO."""
    client = get_minio_client()
    
    try:
        client.remove_object(bucket, object_name)
        logger.debug(
            "Object deleted",
            bucket=bucket,
            object=object_name
        )
        return True
        
    except S3Error as e:
        logger.error(
            "Failed to delete object",
            bucket=bucket,
            object=object_name,
            error=str(e)
        )
        return False


async def object_exists(bucket: str, object_name: str) -> bool:
    """Check if object exists in bucket."""
    client = get_minio_client()
    
    try:
        client.stat_object(bucket, object_name)
        return True
    except S3Error:
        return False


async def list_objects(
    bucket: str,
    prefix: str = "",
    recursive: bool = False
) -> list:
    """List objects in bucket with optional prefix."""
    client = get_minio_client()
    
    try:
        objects = client.list_objects(
            bucket,
            prefix=prefix,
            recursive=recursive
        )
        return [obj.object_name for obj in objects]
        
    except S3Error as e:
        logger.error(
            "Failed to list objects",
            bucket=bucket,
            prefix=prefix,
            error=str(e)
        )
        return []


# Helper functions for surveillance system
async def upload_subject_image(
    subject_id: str,
    image_id: str,
    image_data: bytes,
    image_type: str = "gallery"
) -> str:
    """Upload subject image to subjects bucket."""
    object_name = f"{subject_id}/{image_type}/{image_id}.jpg"
    return await upload_image(
        settings.MINIO_BUCKET_SUBJECTS,
        object_name,
        image_data
    )


async def upload_live_frame(
    camera_id: str,
    frame_id: str,
    image_data: bytes
) -> str:
    """Upload live frame to live bucket."""
    from datetime import datetime
    date_str = datetime.utcnow().strftime("%Y%m%d")
    object_name = f"{camera_id}/{date_str}/{frame_id}.jpg"
    return await upload_image(
        settings.MINIO_BUCKET_LIVE,
        object_name,
        image_data
    )


async def get_subject_image_url(subject_id: str, image_id: str) -> str:
    """Get presigned URL for subject image."""
    object_name = f"{subject_id}/gallery/{image_id}.jpg"
    return await get_presigned_url(
        settings.MINIO_BUCKET_SUBJECTS,
        object_name
    )
