from sqlalchemy.orm import Session
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_model import Patient
from ..models.patient_privacy_level_model import PatientPrivacyLevel
from ..schemas.patient_privacy_level import PatientPrivacyLevelCreate, PatientPrivacyLevelUpdate

def get_privacy_level_by_patient(db: Session, patient_id: int):
    return db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()

def get_privacy_levels_by_patient(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PatientPrivacyLevel).order_by(PatientPrivacyLevel.patientId).offset(skip).limit(limit).all()

def create_patient_privacy_level(db: Session, patient_id: int, patient_privacy_level: PatientPrivacyLevelCreate, created_by: str, user_full_name: str):
    db_privacy_level_setting = PatientPrivacyLevel(**patient_privacy_level.model_dump(),patientId=patient_id,createdById=created_by,modifiedById=created_by)
    db.add(db_privacy_level_setting)
    db.commit()
    db.refresh(db_privacy_level_setting)

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        patient_name = patient.name if patient else None
    except Exception as e:
        patient_name = None

    updated_data_dict = serialize_data(patient_privacy_level.model_dump())
    updated_data_dict['PatientName'] = patient_name

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name= user_full_name,
        message = f"Set privacy level for patient: {patient_name or 'Unknown'}",
        table= "PatientPrivacyLevel",
        entity_id = db_privacy_level_setting.patientId,
        original_data=None,
        updated_data=updated_data_dict,
        patient_id=patient_id,
        patient_full_name= patient_name,
        log_type = "patient_info",
        is_system_config = False
    )
    return db_privacy_level_setting

def update_patient_privacy_level(db: Session, patient_id: int, patient_privacy_level: PatientPrivacyLevelUpdate, modified_by:str, user_full_name: str):
    db_privacy_level_setting = db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()
    if db_privacy_level_setting:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_privacy_level_setting.__dict__.items() if not k.startswith('_')
            }
        except Exception as e:
            original_data_dict = "{}"
        if db_privacy_level_setting.active == 0:
            db_privacy_level_setting.privacyLevelSensitive = 0
        db_privacy_level_setting.modifiedById = modified_by
        # Update only provided fields
        update_data = patient_privacy_level.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_privacy_level_setting, field, value)
        db.commit()
        db.refresh(db_privacy_level_setting)

        # Fetch names for logging
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            patient_name = patient.name if patient else None
        except Exception as e:
            patient_name = None

        updated_data_dict = serialize_data(update_data)
        updated_data_dict['PatientName'] = patient_name
        original_data_dict['PatientName'] = patient_name

        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name= user_full_name,
            message = f"Updated privacy level for patient : {patient_name or 'Unknown'}",
            table= "PatientPrivacyLevel",
            entity_id = db_privacy_level_setting.patientId,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            patient_id=patient_id,
            patient_full_name= patient_name,
            log_type = "patient_info",
            is_system_config = False
        )
    return db_privacy_level_setting

def delete_patient_privacy_level(db: Session, patient_id: int, modified_by: str, user_full_name: str):
    db_privacy_level_setting = db.query(PatientPrivacyLevel).filter(PatientPrivacyLevel.patientId == patient_id).first()
    if db_privacy_level_setting:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_privacy_level_setting.__dict__.items() if not k.startswith('_')
            }
        except Exception as e:
            original_data_dict = "{}"

        # Fetch patient name
        try:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            patient_name = patient.name if patient else None
        except Exception as e:
            patient_name = None

        db.delete(db_privacy_level_setting)
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name= user_full_name,
            message = f"Deleted privacy level for patient : {patient_name or 'Unknown'}",
            table= "PatientPrivacyLevel",
            entity_id = db_privacy_level_setting.patientId,
            original_data=original_data_dict,
            updated_data= None,
            patient_id=patient_id,
            patient_full_name= patient_name,
            log_type = "patient_info",
            is_system_config = False
        )
    return db_privacy_level_setting