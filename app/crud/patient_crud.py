from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime

#To Change
user = 1
def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == '0').first()

def get_patients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Patient).filter(Patient.isDeleted == '0').order_by(Patient.id).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    db_patient = Patient(**patient.model_dump())
    db_patient.modifiedDate = datetime.now()
    db_patient.createdDate = datetime.now()
    db_patient.createdById = user
    db_patient.modifiedById = user
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        for key, value in patient.model_dump().items():
            setattr(db_patient, key, value)
        db_patient.modifiedDate = datetime.now()
        db_patient.modifiedById = user
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        setattr(db_patient, 'isDeleted', '1')
        db.commit()
    return db_patient
