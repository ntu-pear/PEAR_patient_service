from datetime import datetime
from sqlalchemy.orm import Session
from ..models.patient_vital_model import PatientVital
from ..schemas.patient_vital import PatientVitalCreate, PatientVitalUpdate, PatientVitalDelete

def get_latest_vital(db: Session, patient_id: int):
    return db.query(PatientVital).filter(PatientVital.PatientId == patient_id).order_by(PatientVital.CreatedDateTime.desc()).first()

def get_vital_list(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(PatientVital)
        .filter(PatientVital.PatientId == patient_id)
        .order_by(PatientVital.CreatedDateTime.desc())  # Ensure ordering before OFFSET and LIMIT
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def create_vital(db: Session, vital: PatientVitalCreate):
    db_vital = PatientVital(**vital.dict())
    db.add(db_vital)
    db.commit()
    db.refresh(db_vital)
    return db_vital

def update_vital(db: Session, vital_id: int, vital: PatientVitalUpdate):
    db_vital = db.query(PatientVital).filter(PatientVital.Id == vital_id).first()
    if db_vital:
        for key, value in vital.dict().items():
            if key == "UpdatedDateTime":
                setattr(db_vital, key, datetime.now())
            else:
                setattr(db_vital, key, value)
        db.commit()
        db.refresh(db_vital)
    return db_vital

def delete_vital(db: Session, vital_id: int):
    db_vital = db.query(PatientVital).filter(PatientVital.Id == vital_id).first()
    if db_vital:
        setattr(db_vital, "IsDeleted", "0")
        db.commit()
        db.refresh(db_vital)
    return db_vital
