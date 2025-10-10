from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.models.patient_model import Patient
from app.models.patient_medication_model import PatientMedication

router = APIRouter()

@router.get("/patient")
async def get_patient_integrity(
    hours_back: int = Query(1, ge=1, le=168, description="Hours to look back (1-168)"),
    limit: int = Query(1000, ge=1, le=5000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Returns patient] IDs and their last modified timestamps.
    Used by reconciliation service to detect data drift.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        patients = db.query(Patient).filter(
            Patient.modifiedDate >= cutoff_time
        ).order_by(Patient.id).limit(limit).offset(offset).all()
        
        records = []
        for patient in patients:
            records.append({
                "id": patient.id,
                "modified_date": patient.modifiedDate.isoformat(),
                "version_timestamp": int(patient.modifiedDate.timestamp() * 1000),
                "record_type": "patient"
            })
        
        # Get total count for pagination
        total_count = db.query(Patient).filter(
            Patient.modifiedDate >= cutoff_time
        ).count()
        
        return {
            "service": "patient",
            "endpoint": "/integrity/patient",
            "window_hours": hours_back,
            "cutoff_time": cutoff_time.isoformat(),
            "total_count": total_count,
            "returned_count": len(records),
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(records)) < total_count,
            "records": records,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patient integrity check failed: {str(e)}")

@router.get("/patient-medication")
async def get_patient_medication_integrity(
    hours_back: int = Query(1, ge=1, le=168),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns patient medications IDs and their last modified timestamps.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Query patient_medications modified in the time window
        patient_medications = db.query(PatientMedication).filter(
            PatientMedication.UpdatedDateTime >= cutoff_time
        ).order_by(PatientMedication.Id).limit(limit).offset(offset).all()
        
        records = []
        for med in patient_medications:
            # Use UpdatedDateTime if available, otherwise created_date
            last_modified = med.UpdatedDateTime or med.CreatedDateTime
            
            records.append({
                "id": med.Id,
                "patient_id": med.PatientId,
                "modified_date": last_modified.isoformat(),
                "version_timestamp": int(last_modified.timestamp() * 1000),
                "record_type": "patient_medication"
            })
        
        # Total count for pagination
        total_count = db.query(PatientMedication).filter(
            PatientMedication.UpdatedDateTime >= cutoff_time
        ).count()
        
        return {
            "service": "patient",
            "endpoint": "/integrity/patient-medication",
            "window_hours": hours_back,
            "cutoff_time": cutoff_time.isoformat(),
            "total_count": total_count,
            "returned_count": len(records),
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(records)) < total_count,
            "records": records,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patient medication integrity check failed: {str(e)}")

@router.get("/summary")
async def get_integrity_summary(
    hours_back: int = Query(1, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Returns a summary of all patient-related record counts for the specified time window.
    Useful for high-level drift detection and monitoring.
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Count records in each table
        patient_count = db.query(Patient).filter(
            Patient.modifiedDate >= cutoff_time
        ).count()
        
        patient_medication_count = db.query(PatientMedication).filter(
            PatientMedication.UpdatedDateTime >= cutoff_time
        ).count()
        
        return {
            "service": "patient",
            "endpoint": "/integrity/summary",
            "window_hours": hours_back,
            "cutoff_time": cutoff_time.isoformat(),
            "record_counts": {
                "patient": patient_count,
                "patient_medication": patient_medication_count,
                "total": (patient_count + patient_medication_count)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity summary failed: {str(e)}")

# Health check endpoint for the integrity system
@router.get("/health")
async def integrity_health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify integrity system is working.
    """
    try:
        # Test database connectivity
        db.execute(text("SELECT 1"))
        
        # Get recent patient to verify data access
        recent_patient = db.query(Patient).filter(
            Patient.modifiedDate >= datetime.now() - timedelta(hours=24)
        ).first()
        
        return {
            "status": "healthy",
            "service": "patient",
            "database_connected": True,
            "recent_data_available": recent_patient is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Integrity health check failed: {str(e)}")
