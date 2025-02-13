from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.patient_list_language_model import PatientListLanguage
from ..schemas.patient_list_language import PatientListLanguageCreate, PatientListLanguageUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_patient_list_language(db: Session, patient_list_language_id: int):
    db_patient_language =  db.query(PatientListLanguage).filter(PatientListLanguage.id == patient_list_language_id, PatientListLanguage.isDeleted == '0').first()
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")
    return db_patient_language

def get_all_patient_list_language(db: Session):
    return db.query(PatientListLanguage).filter(PatientListLanguage.isDeleted == "0").all()

def create_patient_list_language(
    db: Session, patient_language: PatientListLanguageCreate
):
    existing_language = (
        db.query(PatientListLanguage)
        .filter(PatientListLanguage.value == patient_language.value, 
                PatientListLanguage.isDeleted == "0")
        .first()
    )
    if existing_language:
        raise HTTPException(status_code=400, detail="Language value already exists")
    
    db_language_item = PatientListLanguage(**patient_language.model_dump(), 
                                           createdDate = datetime.now(),
                                           modifiedDate = datetime.now())
    updated_data_dict = serialize_data(patient_language.model_dump())
    db.add(db_language_item)
    db.commit()
    db.refresh(db_language_item)

    log_crud_action(
        action=ActionType.CREATE,
        user=1,
        table="PatientListLanguage",
        entity_id=db_language_item.id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_language_item

def update_patient_list_language(
        db: Session, 
        patient_language_id: int, 
        patient_language: PatientListLanguageUpdate
):
    db_patient_language = (
        db.query(PatientListLanguage)
        .filter(PatientListLanguage.id == patient_language_id, 
                PatientListLanguage.isDeleted == '0')
        .first()
    )
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")

    existing_language = (
        db.query(PatientListLanguage)
        .filter(PatientListLanguage.value == patient_language.value, 
                PatientListLanguage.isDeleted == "0")
        .first()
    )
    if existing_language:
        raise HTTPException(status_code=400, detail="Language value already exists")
    
    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_patient_language.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    for key, value in patient_language.model_dump().items():
        setattr(db_patient_language, key, value)
    db_patient_language.modifiedDate = datetime.now()

    db.commit()
    db.refresh(db_patient_language)

    log_crud_action(
        action=ActionType.UPDATE,
        user=1,
        table="PatientListLanguage",
        entity_id=db_patient_language.id,
        original_data=original_data_dict,
        updated_data=serialize_data(patient_language.model_dump()),
    )
    return db_patient_language

def delete_patient_list_language(db: Session, patient_language_id: int):
    db_patient_language = (
        db.query(PatientListLanguage).
        filter(PatientListLanguage.id == patient_language_id, 
               PatientListLanguage.isDeleted == '0')
        .first()
    )
    if not db_patient_language:
        raise HTTPException(status_code=404, detail="Language Id not found")
    
    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_patient_language.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    db_patient_language.isDeleted = "1"
    db_patient_language.modifiedDate = datetime.now()
    db.commit()
    db.refresh(db_patient_language)

    log_crud_action(
        action=ActionType.DELETE,
        user=1,
        table="PatientListLanguage",
        entity_id=db_patient_language.id,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_patient_language

