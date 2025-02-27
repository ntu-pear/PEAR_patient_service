from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_social_history_crud as crud_social_history
from ..schemas.patient_social_history import (
    PatientSocialHistory,
    PatientSocialHistoryCreate,
    PatientSocialHistoryUpdate,
    PatientSocialHistoryDecode
)

router = APIRouter()

@router.get("/SocialHistory", response_model=PatientSocialHistoryDecode, description="Get social history records by Patient ID.")
def get_social_history(patient_id: int, db: Session = Depends(get_db)):
    db_social_history = crud_social_history.get_patient_social_history(db, patient_id)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    return db_social_history

@router.post("/SocialHistory/add", response_model=PatientSocialHistoryCreate)
def create_social_history(social_history: PatientSocialHistoryCreate, db: Session = Depends(get_db)):
    # TODO: CHANGE USER ID to the actual user ID
    userId = "1"
    return crud_social_history.create_patient_social_history(db, social_history, userId)

@router.put("/SocialHistory/update", response_model=PatientSocialHistoryUpdate)
def update_social_history(patient_id: int, social_history: PatientSocialHistoryUpdate, db: Session = Depends(get_db)):
    # TODO: CHANGE USER ID to the actual user ID
    userId = "1"
    db_social_history = crud_social_history.update_patient_social_history(db, patient_id, social_history, userId)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    return db_social_history

@router.put("/SocialHistory/delete", response_model=PatientSocialHistory)
def delete_social_history(patient_id: int, db: Session = Depends(get_db)):
    """
    Perform a soft delete on the social history record by changing 'isDeleted' from '0' to '1'.
    """
    # TODO: CHANGE USER ID to the actual user ID
    userId = "1"
    return crud_social_history.delete_patient_social_history(db, patient_id, userId)
    
