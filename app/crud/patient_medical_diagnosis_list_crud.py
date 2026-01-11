import math
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_medical_diagnosis_list_model import PatientMedicalDiagnosisList
from ..schemas.patient_medical_diagnosis_list import (
    PatientMedicalDiagnosisListCreate,
    PatientMedicalDiagnosisListUpdate,
)


def get_all_diagnosis_list(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    db_diagnosis_list = db.query(PatientMedicalDiagnosisList).filter(
        PatientMedicalDiagnosisList.IsDeleted == "0"
    ).order_by(PatientMedicalDiagnosisList.DiagnosisName.asc()).offset(offset).limit(pageSize).all()
    
    totalRecords = db.query(func.count()).select_from(PatientMedicalDiagnosisList).filter(
        PatientMedicalDiagnosisList.IsDeleted == "0"
    ).scalar()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    return db_diagnosis_list, totalRecords, totalPages


def get_diagnosis_by_id(db: Session, diagnosis_id: int):
    return db.query(PatientMedicalDiagnosisList).filter(
        PatientMedicalDiagnosisList.Id == diagnosis_id,
        PatientMedicalDiagnosisList.IsDeleted == "0"
    ).first()


def create_diagnosis(db: Session, diagnosis: PatientMedicalDiagnosisListCreate, user_id: str, user_full_name: str):
    db_diagnosis = PatientMedicalDiagnosisList(**diagnosis.model_dump())
    
    if db_diagnosis:
        db_diagnosis.CreatedDate = datetime.now()
        db_diagnosis.ModifiedDate = datetime.now()
        db.add(db_diagnosis)
        db.commit()
        db.refresh(db_diagnosis)

        updated_data_dict = serialize_data(diagnosis.model_dump())

        log_crud_action(
            action=ActionType.CREATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Created medical diagnosis",
            table="Medical Diagnosis List",
            entity_id=None,
            original_data=None,
            updated_data=updated_data_dict
        )
    
    return db_diagnosis


def update_diagnosis(db: Session, diagnosis_id: int, diagnosis: PatientMedicalDiagnosisListUpdate, user_id: str, user_full_name: str):
    db_diagnosis = db.query(PatientMedicalDiagnosisList).filter(
        PatientMedicalDiagnosisList.Id == diagnosis_id
    ).first()

    if db_diagnosis:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_diagnosis.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in diagnosis.model_dump(exclude_unset=True).items():
            setattr(db_diagnosis, key, value)

        db_diagnosis.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_diagnosis)

        updated_data_dict = serialize_data(diagnosis.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Updated medical diagnosis",
            table="Medical Diagnosis List",
            entity_id=diagnosis_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )

    return db_diagnosis


def delete_diagnosis(db: Session, diagnosis_id: int, user_id: str, user_full_name: str):
    db_diagnosis = db.query(PatientMedicalDiagnosisList).filter(
        PatientMedicalDiagnosisList.Id == diagnosis_id
    ).first()

    if db_diagnosis:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_diagnosis.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        db_diagnosis.IsDeleted = "1"
        db_diagnosis.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_diagnosis)

        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message="Deleted medical diagnosis",
            table="Medical Diagnosis List",
            entity_id=diagnosis_id,
            original_data=original_data_dict,
            updated_data=None
        )

    return db_diagnosis