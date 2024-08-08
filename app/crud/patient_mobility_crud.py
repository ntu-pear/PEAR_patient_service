from sqlalchemy.orm import Session
from ..models.patient_mobility_model import PatientMobility
from ..schemas.patient_mobility import PatientMobilityCreate, PatientMobilityUpdate

def get_patient_mobility(db: Session, patient_id: int):
    return db.query(PatientMobility).filter(PatientMobility.patient_id == patient_id).all()

def create_patient_mobility(db: Session, mobility: PatientMobilityCreate):
    db_mobility = PatientMobility(**mobility.dict())
    db.add(db_mobility)
    db.commit()
    db.refresh(db_mobility)
    return db_mobility

def update_patient_mobility(db: Session, mobility_id: int, mobility: PatientMobilityUpdate):
    db_mobility = db.query(PatientMobility).filter(PatientMobility.id == mobility_id).first()
    if db_mobility:
        for key, value in mobility.dict().items():
            setattr(db_mobility, key, value)
        db.commit()
        db.refresh(db_mobility)
    return db_mobility

def delete_patient_mobility(db: Session, mobility_id: int, mobility: PatientMobilityUpdate):
    db_mobility = db.query(PatientMobility).filter(PatientMobility.id == mobility_id).first()
    if db_mobility:
        for key, value in mobility.dict().items():
            setattr(db_mobility, key, value)
        db.commit()
        db.refresh(db_mobility)
    return db_mobility
