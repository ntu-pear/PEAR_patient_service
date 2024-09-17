from http.client import HTTPException
from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..models.patient_list_language_model import PatientListLanguage
from ..models.patient_patient_list_language_model import Patient_PatientListLanguage
from ..schemas.patient import PatientCreate, PatientUpdate, PatientLanguageCreate

def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Patient).order_by(Patient.id).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_patient_language(db: Session, patient_language: PatientLanguageCreate):
    language_record = db.query(PatientListLanguage).filter(
        PatientListLanguage.value == patient_language.language
    ).first()

    if not language_record:
        return None
    
    new_record = Patient_PatientListLanguage(
        patientId=patient_language.patient_id,
        listLanguageId=language_record.id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def update_patient(db: Session, patient_id: int, patient: PatientUpdate):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        for key, value in patient.dict().items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
    return db_patient
