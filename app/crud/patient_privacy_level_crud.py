from sqlalchemy.orm import Session
from ..models.patient_privacy_level_model import PatientPrivacyLevel
from ..schemas.patient_privacy_level import PatientPrivacyLevelCreate, PatientPrivacyLevelUpdate

def get_privacy_level_by_patient(db: Session, patient_id: int):
    return db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()

def get_privacy_levels_by_patient(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PatientPrivacyLevel).order_by(PatientPrivacyLevel.patientId).offset(skip).limit(limit).all()

def create_patient_privacy_level(db: Session, patient_id: int, patient_privacy_level: PatientPrivacyLevelCreate, created_by: str):
    db_privacy_level_setting = PatientPrivacyLevel(**patient_privacy_level.model_dump(),patientId=patient_id,createdById=created_by,modifiedById=created_by)
    db.add(db_privacy_level_setting)
    db.commit()
    db.refresh(db_privacy_level_setting)
    return db_privacy_level_setting

def update_patient_privacy_level(db: Session, patient_id: int, patient_privacy_level: PatientPrivacyLevelUpdate, modified_by:str):
    db_privacy_level_setting = db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()
    if db_privacy_level_setting:
        if db_privacy_level_setting.active == 0:
            db_privacy_level_setting.privacyLevelSensitive = 0
        db_privacy_level_setting.modifiedById = modified_by
        # Update only provided fields
        for field, value in patient_privacy_level.model_dump(exclude_unset=True).items():
            setattr(db_privacy_level_setting, field, value)
        db.commit()
        db.refresh(db_privacy_level_setting)
    return db_privacy_level_setting

def delete_patient_privacy_level(db: Session, patient_id: int):
    db_privacy_level_setting = db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()
    if db_privacy_level_setting:
        db.delete(db_privacy_level_setting)
        db.commit()
    return db_privacy_level_setting