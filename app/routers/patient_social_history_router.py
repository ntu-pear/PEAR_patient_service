from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_social_history_crud as crud_social_history
from ..schemas import patient_social_history as schemas_social_history

router = APIRouter()

@router.get("/SocialHistory", response_model=schemas_social_history.PatientSocialHistory)
def get_social_history(patient_id: int, db: Session = Depends(get_db)):
    db_social_history = crud_social_history.get_social_history(db, patient_id)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    return db_social_history

@router.post("/SocialHistory/add", response_model=schemas_social_history.PatientSocialHistory)
def create_social_history(social_history: schemas_social_history.PatientSocialHistoryCreate, db: Session = Depends(get_db)):
    return crud_social_history.create_social_history(db, social_history)

@router.put("/SocialHistory/update", response_model=schemas_social_history.PatientSocialHistory)
def update_social_history(social_history_id: int, social_history: schemas_social_history.PatientSocialHistoryUpdate, db: Session = Depends(get_db)):
    db_social_history = crud_social_history.update_social_history(db, social_history_id, social_history)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    return db_social_history

@router.put("/SocialHistory/delete", response_model=schemas_social_history.PatientSocialHistory)
def delete_social_history(social_history_id: int, db: Session = Depends(get_db)):
    """
    Perform a soft delete on the social history record by changing 'active' from 'Y' to 'N'.
    """
    db_social_history = db.query(crud_social_history.PatientSocialHistory).filter(crud_social_history.PatientSocialHistory.patientId == social_history_id).first()
    
    if db_social_history:
        # Perform the soft delete by setting 'active' to 'N'
        db_social_history.isDeleted = '1'
        db.commit()
        db.refresh(db_social_history)
        return db_social_history
    else:
        raise HTTPException(status_code=404, detail="Social history not found")
