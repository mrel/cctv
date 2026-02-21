"""Main API router that includes all endpoint modules."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    cameras,
    subjects,
    images,
    sightings,
    alerts,
    analytics,
    users,
    websocket
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(images.router, prefix="/images", tags=["Images"])
api_router.include_router(sightings.router, prefix="/sightings", tags=["Sightings"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
