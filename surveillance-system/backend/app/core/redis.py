"""
Redis client configuration for caching and message queuing.
Uses aioredis for async operations.
"""

import json
from typing import Any, Optional, List

import aioredis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Global Redis client
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client
    logger.info("Initializing Redis connection...")
    
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_POOL_SIZE
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established")
        
    except Exception as e:
        logger.error("Failed to initialize Redis", error=str(e))
        raise


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    logger.info("Closing Redis connection...")
    
    if redis_client:
        await redis_client.close()
        redis_client = None
    
    logger.info("Redis connection closed")


def get_redis() -> aioredis.Redis:
    """Get Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


# Cache operations
async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        value = await get_redis().get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning("Cache get failed", key=key, error=str(e))
        return None


async def cache_set(key: str, value: Any, expire: int = 300) -> bool:
    """Set value in cache with expiration (seconds)."""
    try:
        await get_redis().setex(key, expire, json.dumps(value))
        return True
    except Exception as e:
        logger.warning("Cache set failed", key=key, error=str(e))
        return False


async def cache_delete(key: str) -> bool:
    """Delete value from cache."""
    try:
        await get_redis().delete(key)
        return True
    except Exception as e:
        logger.warning("Cache delete failed", key=key, error=str(e))
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """Delete keys matching pattern."""
    try:
        keys = await get_redis().keys(pattern)
        if keys:
            return await get_redis().delete(*keys)
        return 0
    except Exception as e:
        logger.warning("Cache delete pattern failed", pattern=pattern, error=str(e))
        return 0


# Stream operations for message queuing
async def stream_add(stream: str, data: dict) -> str:
    """Add message to Redis Stream."""
    redis = get_redis()
    message_id = await redis.xadd(stream, data)
    return message_id


async def stream_read(
    stream: str,
    group: Optional[str] = None,
    consumer: Optional[str] = None,
    count: int = 10,
    block: int = 5000,
    last_id: str = ">"
) -> List[dict]:
    """Read messages from Redis Stream."""
    redis = get_redis()
    
    if group and consumer:
        messages = await redis.xreadgroup(
            group,
            consumer,
            {stream: last_id},
            count=count,
            block=block
        )
    else:
        messages = await redis.xread(
            {stream: last_id},
            count=count,
            block=block
        )
    
    return messages


async def stream_ack(stream: str, group: str, message_id: str) -> int:
    """Acknowledge message in consumer group."""
    redis = get_redis()
    return await redis.xack(stream, group, message_id)


async def stream_create_group(stream: str, group: str) -> bool:
    """Create consumer group for stream."""
    redis = get_redis()
    try:
        await redis.xgroup_create(stream, group, id="0", mkstream=True)
        return True
    except aioredis.ResponseError as e:
        if "already exists" in str(e):
            return True
        raise


# Pub/Sub operations
async def publish(channel: str, message: dict) -> int:
    """Publish message to channel."""
    redis = get_redis()
    return await redis.publish(channel, json.dumps(message))


# Rate limiting
async def check_rate_limit(key: str, max_requests: int, window: int) -> tuple[bool, int]:
    """
    Check if request is within rate limit.
    Returns (allowed, remaining_requests).
    """
    redis = get_redis()
    
    pipe = redis.pipeline()
    now = await redis.time()
    current_time = now[0]
    window_key = f"{key}:{current_time // window}"
    
    pipe.incr(window_key)
    pipe.expire(window_key, window)
    results = await pipe.execute()
    
    current_count = results[0]
    remaining = max(0, max_requests - current_count)
    
    return current_count <= max_requests, remaining
