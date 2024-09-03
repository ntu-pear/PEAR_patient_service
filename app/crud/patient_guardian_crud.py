from sqlalchemy.orm import Session
from ..models.patient_guardian_model import PatientGuardian
from ..schemas.patient_guardian import PatientGuardianCreate, PatientGuardianUpdate

def get_guardian(db: Session, guardian_id: int):
    return db.query(PatientGuardian).filter(PatientGuardian.id == guardian_id).first()

def get_guardian_by_nric(db: Session, nric: str):
    return db.query(PatientGuardian).filter(PatientGuardian.nric == nric).first()

def get_patient_guardian(db: Session, patient_id: int):
    return db.query(PatientGuardian).filter(PatientGuardian.patientId == patient_id).all()

def create_guardian(db: Session, guardian: PatientGuardianCreate):
    db_guardian = PatientGuardian(**guardian.dict())
    db.add(db_guardian)
    db.commit()
    db.refresh(db_guardian)
    return db_guardian

def update_guardian(db: Session, guardian_id: int, guardian: PatientGuardianUpdate):
    db_guardian = db.query(PatientGuardian).filter(PatientGuardian.id == guardian_id).first()
    if db_guardian:
        for key, value in guardian.dict().items():
            setattr(db_guardian, key, value)
        db.commit()
        db.refresh(db_guardian)
    return db_guardian

def delete_guardian(db: Session, guardian_id: int):
    db_guardian = db.query(PatientGuardian).filter(PatientGuardian.id == guardian_id).first()
    if db_guardian:
        setattr(db_guardian, 'isDeleted', '1')
        db.commit()
        db.refresh(db_guardian)
    return db_guardian
