from sqlalchemy.orm import Session
from ..models.patient_social_history_model import PatientSocialHistory
from ..schemas.patient_social_history import PatientSocialHistoryCreate, PatientSocialHistoryUpdate

def get_social_history(db: Session, patient_id: int):
    return db.query(PatientSocialHistory).filter(PatientSocialHistory.patientId == patient_id).first()

def create_social_history(db: Session, social_history: PatientSocialHistoryCreate):
    db_social_history = PatientSocialHistory(**social_history.dict())
    db.add(db_social_history)
    db.commit()
    db.refresh(db_social_history)
    return db_social_history

def update_social_history(db: Session, social_history_id: int, social_history: PatientSocialHistoryUpdate):
    db_social_history = db.query(PatientSocialHistory).filter(PatientSocialHistory.id == social_history_id).first()
    if db_social_history:
        for key, value in social_history.dict().items():
            setattr(db_social_history, key, value)
        db.commit()
        db.refresh(db_social_history)
    return db_social_history

def delete_social_history(db: Session, social_history_id: int, social_history: PatientSocialHistoryUpdate):
    db_social_history = db.query(PatientSocialHistory).filter(PatientSocialHistory.id == social_history_id).first()
    if db_social_history:
        for key, value in social_history.dict().items():
            setattr(db_social_history, key, value)
        db.commit()
        db.refresh(db_social_history)
    return db_social_history
