from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.patient_list_language_model import PatientListLanguage
from ..schemas.patient_list_language import PatientListLanguageCreate, PatientListLanguageUpdate
from datetime import datetime

def get_patient_list_language(db: Session, patient_list_language_id: int):
    db_patient_language =  db.query(PatientListLanguage).filter(PatientListLanguage.id == patient_list_language_id, PatientListLanguage.isDeleted == '0').first()
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")
    return db_patient_language

def get_all_patient_list_language(db: Session):
    return db.query(PatientListLanguage).filter(PatientListLanguage.isDeleted == "0").all()

def create_patient_list_language(db: Session, patient_language: PatientListLanguageCreate):
    existing_language = db.query(PatientListLanguage).filter(PatientListLanguage.value == patient_language.value, PatientListLanguage.isDeleted == "0").first()
    if existing_language:
        raise HTTPException(status_code=400, detail="Language value already exists")
    
    db_language_item = PatientListLanguage(**patient_language.model_dump(), 
                                           createdDate = datetime.now(),
                                           modifiedDate = datetime.now())
    db.add(db_language_item)
    db.commit()
    db.refresh(db_language_item)
    return db_language_item

def update_patient_list_language(db: Session, patient_language_id: int, patient_language: PatientListLanguageUpdate):
    db_patient_language = db.query(PatientListLanguage).filter(PatientListLanguage.id == patient_language_id, PatientListLanguage.isDeleted == '0').first()
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")

    existing_language = db.query(PatientListLanguage).filter(PatientListLanguage.value == patient_language.value, PatientListLanguage.isDeleted == "0").first()
    if existing_language:
        raise HTTPException(status_code=400, detail="Language value already exists")
    
    for key, value in patient_language.model_dump().items():
        setattr(db_patient_language, key, value)
    db_patient_language.modifiedDate = datetime.now()

    db.commit()
    db.refresh(db_patient_language)
    return db_patient_language

def delete_patient_list_language(db: Session, patient_language_id: int):
    db_patient_language = db.query(PatientListLanguage).filter(PatientListLanguage.id == patient_language_id, PatientListLanguage.isDeleted == '0').first()
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")
    
    db_patient_language.isDeleted = "1"
    db_patient_language.modifiedDate = datetime.now()
    db.commit()
    db.refresh(db_patient_language)
    return db_patient_language

