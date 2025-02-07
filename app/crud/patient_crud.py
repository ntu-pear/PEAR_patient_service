from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime

#To Change
user = 1
def mask_nric(nric: str):
    return ('*' * 5) + nric[-4:]

def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == '0').first()
    if db_patient and mask:
        db_patient.nric = mask_nric(db_patient.nric)
    return db_patient

def get_patients(db: Session, mask: bool = True, skip: int = 0, limit: int = 10):
    db_patients = db.query(Patient).filter(Patient.isDeleted == '0').order_by(Patient.id).offset(skip).limit(limit).all()
    total = total = db.query(func.count()).select_from(Patient).filter(Patient.isDeleted == '0').scalar()
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = mask_nric(db_patient.nric)
    return db_patients, total

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
