"""Audit logging middleware for GDPR compliance."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
import time

from app.core.database import AsyncSessionLocal
from app.models.audit import AuditLog

logger = structlog.get_logger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests for audit trail."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log to audit trail."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Skip logging for certain paths
        if self._should_skip_logging(request):
            return response
        
        # Log to audit trail (async fire-and-forget)
        try:
            await self._log_request(request, response, time.time() - start_time)
        except Exception as e:
            logger.warning("Failed to log audit entry", error=str(e))
        
        return response
    
    def _should_skip_logging(self, request: Request) -> bool:
        """Check if request should be skipped from audit log."""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static/",
            "/api/v1/ws/"
        ]
        
        path = request.url.path
        return any(path.startswith(skip) for skip in skip_paths)
    
    async def _log_request(
        self,
        request: Request,
        response,
        duration: float
    ):
        """Create audit log entry."""
        # Determine action from request
        action = self._determine_action(request)
        
        if not action:
            return
        
        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        user_role = getattr(request.state, "user_role", None)
        
        # Create audit log
        async with AsyncSessionLocal() as session:
            audit_log = AuditLog(
                user_id=user_id,
                user_role=user_role,
                action=action,
                resource_type=self._determine_resource_type(request),
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "duration_ms": round(duration * 1000, 2),
                    "status_code": response.status_code
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                compliance_context={
                    "lawful_basis": "legitimate_interest",
                    "retention_days": 365
                }
            )
            
            session.add(audit_log)
            await session.commit()
    
    def _determine_action(self, request: Request) -> str:
        """Determine audit action from request."""
        path = request.url.path
        method = request.method
        
        # Map paths to actions
        action_map = {
            ("GET", "/api/v1/subjects"): "view_subject",
            ("POST", "/api/v1/subjects"): "create_subject",
            ("PUT", "/api/v1/subjects"): "update_subject",
            ("DELETE", "/api/v1/subjects"): "delete_subject",
            ("GET", "/api/v1/cameras"): "view_camera",
            ("POST", "/api/v1/cameras"): "create_camera",
            ("PUT", "/api/v1/cameras"): "update_camera",
            ("DELETE", "/api/v1/cameras"): "delete_camera",
            ("GET", "/api/v1/alerts"): "view_alert",
            ("POST", "/api/v1/alerts"): "acknowledge_alert",
        }
        
        for (m, p), action in action_map.items():
            if method == m and path.startswith(p):
                return action
        
        return None
    
    def _determine_resource_type(self, request: Request) -> str:
        """Determine resource type from request path."""
        path = request.url.path
        
        if "/subjects" in path:
            return "subject"
        elif "/cameras" in path:
            return "camera"
        elif "/alerts" in path:
            return "alert"
        elif "/images" in path:
            return "image"
        elif "/users" in path:
            return "user"
        
        return "system"
