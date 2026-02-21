"""Alert management endpoints."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import publish, cache_delete_pattern
from app.models.alert import AlertRule, AlertLog
from app.models.camera import Camera
from app.models.subject import Subject
from app.schemas.alert import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertLogResponse, AlertAcknowledgeRequest, AlertResolveRequest,
    AlertStatsResponse
)
from app.api.deps import get_current_user, require_permission

router = APIRouter()


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    rule_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all alert rules."""
    query = select(AlertRule)
    
    if is_active is not None:
        query = query.where(AlertRule.is_active == is_active)
    
    if rule_type:
        query = query.where(AlertRule.rule_type == rule_type)
    
    query = query.order_by(desc(AlertRule.priority)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return [AlertRuleResponse.from_orm(r) for r in rules]


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("alerts:write"))
):
    """Create a new alert rule."""
    db_rule = AlertRule(
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        conditions=rule.conditions.dict(),
        actions=rule.actions.dict() if rule.actions else None,
        is_active=rule.is_active,
        priority=rule.priority,
        cooldown_seconds=rule.cooldown_seconds,
        created_by=current_user.user_id
    )
    
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    
    return AlertRuleResponse.from_orm(db_rule)


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert rule by ID."""
    result = await db.execute(
        select(AlertRule).where(AlertRule.rule_id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    return AlertRuleResponse.from_orm(rule)


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: UUID,
    rule_update: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("alerts:write"))
):
    """Update alert rule by ID."""
    result = await db.execute(
        select(AlertRule).where(AlertRule.rule_id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    update_data = rule_update.dict(exclude_unset=True)
    
    if "conditions" in update_data and update_data["conditions"]:
        update_data["conditions"] = update_data["conditions"].dict()
    
    if "actions" in update_data and update_data["actions"]:
        update_data["actions"] = update_data["actions"].dict()
    
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    
    return AlertRuleResponse.from_orm(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("alerts:write"))
):
    """Delete alert rule by ID."""
    result = await db.execute(
        select(AlertRule).where(AlertRule.rule_id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )
    
    await db.delete(rule)
    await db.commit()
    
    return None


@router.get("/logs", response_model=List[AlertLogResponse])
async def list_alert_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    rule_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    camera_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List alert logs with filtering."""
    # Use the active_alerts view for better performance
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM active_alerts
        WHERE 1=1
        AND (:status IS NULL OR status = :status)
        AND (:rule_id IS NULL OR rule_id = :rule_id)
        AND (:subject_id IS NULL OR subject_id = :subject_id)
        AND (:camera_id IS NULL OR camera_id = :camera_id)
        ORDER BY priority DESC, created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    result = await db.execute(query, {
        "status": status,
        "rule_id": str(rule_id) if rule_id else None,
        "subject_id": str(subject_id) if subject_id else None,
        "camera_id": str(camera_id) if camera_id else None,
        "limit": limit,
        "skip": skip
    })
    
    alerts = []
    for row in result:
        alerts.append(AlertLogResponse(
            alert_id=row.alert_id,
            rule_id=row.rule_id,
            rule_name=row.rule_name,
            rule_type=row.rule_type,
            subject_id=row.subject_id,
            subject_label=row.subject_label,
            camera_id=row.camera_id,
            camera_name=row.camera_name,
            trigger_data=row.trigger_data,
            status=row.status,
            priority=row.priority,
            acknowledged_by=row.acknowledged_by,
            acknowledged_at=row.acknowledged_at,
            resolved_at=row.resolved_at,
            notes=row.notes,
            created_at=row.created_at,
            age_minutes=row.age_minutes
        ))
    
    return alerts


@router.get("/logs/{alert_id}", response_model=AlertLogResponse)
async def get_alert_log(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert log by ID."""
    result = await db.execute(
        select(AlertLog).where(AlertLog.alert_id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return AlertLogResponse.from_orm(alert)


@router.post("/logs/{alert_id}/acknowledge", response_model=AlertLogResponse)
async def acknowledge_alert(
    alert_id: UUID,
    request: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("alerts:write"))
):
    """Acknowledge an alert."""
    result = await db.execute(
        select(AlertLog).where(AlertLog.alert_id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.acknowledge(str(current_user.user_id))
    if request.notes:
        alert.notes = request.notes
    
    await db.commit()
    await db.refresh(alert)
    
    # Publish to WebSocket
    await publish("alerts:updates", {
        "type": "acknowledged",
        "alert_id": str(alert_id),
        "acknowledged_by": str(current_user.user_id)
    })
    
    return AlertLogResponse.from_orm(alert)


@router.post("/logs/{alert_id}/resolve", response_model=AlertLogResponse)
async def resolve_alert(
    alert_id: UUID,
    request: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_permission("alerts:write"))
):
    """Resolve an alert."""
    result = await db.execute(
        select(AlertLog).where(AlertLog.alert_id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.resolve()
    if request.notes:
        alert.notes = request.notes
    
    await db.commit()
    await db.refresh(alert)
    
    # Publish to WebSocket
    await publish("alerts:updates", {
        "type": "resolved",
        "alert_id": str(alert_id)
    })
    
    return AlertLogResponse.from_orm(alert)


@router.get("/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert statistics."""
    # Total alerts
    total_result = await db.execute(select(func.count(AlertLog.alert_id)))
    total_alerts = total_result.scalar()
    
    # Status breakdown
    status_result = await db.execute(
        select(AlertLog.status, func.count(AlertLog.alert_id))
        .group_by(AlertLog.status)
    )
    status_counts = {row[0]: row[1] for row in status_result}
    
    # Priority breakdown
    priority_result = await db.execute(
        select(AlertLog.priority, func.count(AlertLog.alert_id))
        .group_by(AlertLog.priority)
    )
    priority_counts = {row[0] or 0: row[1] for row in priority_result}
    
    # Rule type breakdown
    type_result = await db.execute(
        select(AlertRule.rule_type, func.count(AlertLog.alert_id))
        .join(AlertLog, AlertRule.rule_id == AlertLog.rule_id)
        .group_by(AlertRule.rule_type)
    )
    type_counts = {row[0] or "unknown": row[1] for row in type_result}
    
    return AlertStatsResponse(
        total_alerts=total_alerts,
        open_alerts=status_counts.get("open", 0),
        acknowledged_alerts=status_counts.get("acknowledged", 0),
        resolved_alerts=status_counts.get("resolved", 0),
        false_positive_alerts=status_counts.get("false_positive", 0),
        alerts_by_priority=priority_counts,
        alerts_by_rule_type=type_counts
    )
