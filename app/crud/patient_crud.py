from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
from fastapi import HTTPException
#To Change
user = 1

def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == '0').first()
    if db_patient and mask:
        db_patient.nric = db_patient.mask_nric
    return db_patient

def get_patients(db: Session, mask: bool = True, skip: int = 0, limit: int = 10):
    db_patients = db.query(Patient).filter(Patient.isDeleted == '0').order_by(Patient.id).offset(skip).limit(limit).all()
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    return db_patients

def create_patient(db: Session, patient: PatientCreate):
    #Check nric uniqueness
    db_patient_with_same_nric = db.query(Patient).filter(Patient.nric == patient.nric, Patient.isDeleted == '0').first()
    if db_patient_with_same_nric:
        raise HTTPException(status_code=400, detail=f"Nric must be unique for active records")
    
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
        #Check nric uniqueness
        db_patient_with_same_nric = db.query(Patient).filter(Patient.id != patient_id, Patient.nric == patient.nric, Patient.isDeleted == '0').first()
        if db_patient_with_same_nric:
            raise HTTPException(status_code=400, detail=f"Nric must be unique for active records")
        
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
