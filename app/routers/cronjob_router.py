from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.patient_highlight_crud import cleanup_old_highlights
from app.database import get_db

router = APIRouter(prefix="/cronjobs", tags=["Cronjobs"])


@router.post("/highlight-cleanup/run")
def trigger_highlight_cleanup(db: Session = Depends(get_db)):
    """
    Trigger highlight cleanup job.
    
    Called by Kubernetes CronJob daily at midnight.
    Deletes highlights older than 3 days
    
    Returns:
        dict: Cleanup results including number deleted
    """
    result = cleanup_old_highlights(db)
    return {
        "status": "success",
        "message": "Highlight cleanup executed successfully",
        "result": result
    }