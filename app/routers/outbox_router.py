from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..services.outbox_service import get_outbox_service
from ..services.background_processor import get_processor
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..models.outbox_model import OutboxEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outbox", tags=["Outbox Management"])

@router.get("/health")
async def get_health(request: Request, require_auth: bool = True):
    """Get outbox system health status"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        outbox_service = get_outbox_service()
        processor = get_processor()
        
        outbox_stats = outbox_service.get_stats()
        processor_stats = processor.get_stats()
        
        # Simple health check - healthy if processor is running and not too many failures
        is_healthy = (
            processor.is_running() and 
            outbox_stats.get('failed', 0) < 100
        )
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "outbox": outbox_stats,
            "processor": processor_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/stats")
async def get_stats(request: Request, require_auth: bool = True):
    """Get outbox statistics (requires auth)"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        outbox_service = get_outbox_service()
        processor = get_processor()
        
        return {
            "outbox": outbox_service.get_stats(),
            "processor": processor.get_stats()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/events")
async def get_events(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, description="Maximum events to return", ge=1, le=500),
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """Get outbox events with optional filters"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        query = db.query(OutboxEvent)
        
        if status:
            query = query.filter(OutboxEvent.status == status)
        if event_type:
            query = query.filter(OutboxEvent.event_type == event_type)
        
        events = query.order_by(OutboxEvent.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "status": event.status,
                "retry_count": event.retry_count,
                "correlation_id": event.correlation_id,
                "created_at": event.created_at.isoformat(),
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
                "created_by": event.created_by,
                "error_message": event.error_message
            }
            for event in events
        ]
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get events")


@router.get("/events/{event_id}")
async def get_event_detail(
    request: Request,
    event_id: str,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """Get detailed event information including payload"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "id": event.id,
            "event_type": event.event_type,
            "aggregate_id": event.aggregate_id,
            "status": event.status,
            "retry_count": event.retry_count,
            "correlation_id": event.correlation_id,
            "routing_key": event.routing_key,
            "payload": event.get_payload(),
            "created_at": event.created_at.isoformat(),
            "processed_at": event.processed_at.isoformat() if event.processed_at else None,
            "created_by": event.created_by,
            "error_message": event.error_message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event detail: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get event detail")


@router.post("/retry-failed")
async def retry_failed_events(request: Request, require_auth: bool = True):
    """Retry all failed events"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        outbox_service = get_outbox_service()
        count = outbox_service.retry_failed_events()
        return {"message": f"Reset {count} failed events for retry"}
    except Exception as e:
        logger.error(f"Error retrying failed events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retry events")


@router.post("/process-now")
async def process_now(
    request: Request,
    batch_size: int = Query(50, description="Batch size", ge=1, le=200),
    require_auth: bool = True
):
    """Manually trigger event processing"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        outbox_service = get_outbox_service()
        successful, failed = outbox_service.process_pending_events(batch_size)
        return {
            "message": "Processing completed",
            "successful": successful,
            "failed": failed,
            "total": successful + failed
        }
    except Exception as e:
        logger.error(f"Error in manual processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process events")


@router.post("/cleanup")
async def cleanup_old_events(
    request: Request,
    days: int = Query(7, description="Delete events older than this many days", ge=1, le=365),
    require_auth: bool = True
):
    """Clean up old processed events"""
    _ = extract_jwt_payload(request, require_auth)
    try:
        from ..database import SessionLocal
        from ..models.outbox_model import OutboxStatus
        from datetime import timedelta
        
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old published events
            deleted_events = db.query(OutboxEvent).filter(
                OutboxEvent.status == OutboxStatus.PUBLISHED,
                OutboxEvent.created_at < cutoff_date
            ).all()
            
            for event in deleted_events:
                db.delete(event)
            
            db.commit()
            count = len(deleted_events)
            
            return {
                "message": f"Cleaned up {count} old events",
                "deleted_count": count,
                "cutoff_date": cutoff_date.isoformat()
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup events")


# Export router
outbox_router = router