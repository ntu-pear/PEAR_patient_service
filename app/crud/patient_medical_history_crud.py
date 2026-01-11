import math
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_medical_history_model import PatientMedicalHistory
from ..schemas.patient_medical_history import (
    PatientMedicalHistoryCreate,
    PatientMedicalHistoryUpdate,
)


def get_medical_histories_by_patient(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    db_medical_histories = db.query(PatientMedicalHistory).options(
        joinedload(PatientMedicalHistory._diagnosis)
    ).filter(
        PatientMedicalHistory.PatientID == patient_id,
        PatientMedicalHistory.IsDeleted == '0'
    ).order_by(PatientMedicalHistory.Id.desc()).offset(offset).limit(pageSize).all()
    
    totalRecords = db.query(func.count()).select_from(PatientMedicalHistory).filter(
        PatientMedicalHistory.PatientID == patient_id,
        PatientMedicalHistory.IsDeleted == '0'
    ).scalar()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    return db_medical_histories, totalRecords, totalPages


def get_medical_history_by_id(db: Session, history_id: int):
    return db.query(PatientMedicalHistory).options(
        joinedload(PatientMedicalHistory._diagnosis)
    ).filter(
        PatientMedicalHistory.Id == history_id,
        PatientMedicalHistory.IsDeleted == '0'
    ).first()


def create_medical_history(db: Session, medical_history: PatientMedicalHistoryCreate, user_id: str, user_full_name: str):
    db_medical_history = PatientMedicalHistory(**medical_history.model_dump())
    
    if db_medical_history:
        db_medical_history.CreatedDate = datetime.now()
        db_medical_history.ModifiedDate = datetime.now()
        db.add(db_medical_history)
        db.commit()
        db.refresh(db_medical_history)

        updated_data_dict = serialize_data(medical_history.model_dump())

        log_crud_action(
            action=ActionType.CREATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Created patient medical history",
            table="Patient Medical History",
            entity_id=None,
            original_data=None,
            updated_data=updated_data_dict
        )
    
    return db_medical_history


def update_medical_history(db: Session, history_id: int, medical_history: PatientMedicalHistoryUpdate, user_id: str, user_full_name: str):
    db_medical_history = db.query(PatientMedicalHistory).filter(
        PatientMedicalHistory.Id == history_id
    ).first()

    if db_medical_history:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_medical_history.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in medical_history.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(db_medical_history, key, value)

        db_medical_history.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_medical_history)

        updated_data_dict = serialize_data(medical_history.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Updated patient medical history",
            table="Patient Medical History",
            entity_id=history_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )

    return db_medical_history


def delete_medical_history(db: Session, history_id: int, user_id: str, user_full_name: str):
    db_medical_history = db.query(PatientMedicalHistory).filter(
        PatientMedicalHistory.Id == history_id
    ).first()

    if db_medical_history:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_medical_history.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        db_medical_history.IsDeleted = '1'
        db_medical_history.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_medical_history)

        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message="Deleted patient medical history",
            table="Patient Medical History",
            entity_id=history_id,
            original_data=original_data_dict,
            updated_data=None
        )

    return db_medical_history