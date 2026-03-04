import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_medical_history_model import PatientMedicalHistory
from ..models.patient_model import Patient
from ..models.patient_medical_diagnosis_list_model import PatientMedicalDiagnosisList
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
    
    existing = db.query(PatientMedicalHistory).filter(
        PatientMedicalHistory.PatientID == medical_history.PatientID,
        PatientMedicalHistory.MedicalDiagnosisID == medical_history.MedicalDiagnosisID,
        PatientMedicalHistory.IsDeleted == "0"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This patient already has a medical history record for this diagnosis"
        )
    
    
    if db_medical_history:
        db_medical_history.CreatedDate = datetime.now()
        db_medical_history.ModifiedDate = datetime.now()
        db.add(db_medical_history)
        db.commit()
        db.refresh(db_medical_history)

        # Fetch names for logging
        patient = db.query(Patient).filter(Patient.id == medical_history.PatientID).first()
        patient_name = patient.name if patient else None

        diagnosis = db.query(PatientMedicalDiagnosisList).filter(
            PatientMedicalDiagnosisList.Id == medical_history.MedicalDiagnosisID
        ).first()
        diagnosis_name = diagnosis.DiagnosisName if diagnosis else None

        updated_data_dict = serialize_data(medical_history.model_dump())

        log_crud_action(
            action=ActionType.CREATE,
            user=user_id,
            user_full_name=user_full_name,
            message=f"Created medical history: {diagnosis_name} for {patient_name}",
            table="PatientMedicalHistory",
            entity_id=db_medical_history.Id,
            original_data=None,
            updated_data=updated_data_dict,
            patient_id=medical_history.PatientID,
            patient_full_name=patient_name,
            log_type = "medical_history",
            is_system_config=False,
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

        # Fetch old diagnosis name before update
        old_diagnosis = db.query(PatientMedicalDiagnosisList).filter(
            PatientMedicalDiagnosisList.Id == db_medical_history.MedicalDiagnosisID
        ).first()
        old_diagnosis_name = old_diagnosis.DiagnosisName if old_diagnosis else None

        update_data = medical_history.model_dump(exclude_unset=True)

        # Duplicate check if PatientID or MedicalDiagnosisID is being changed
        new_patient_id = update_data.get("PatientID", db_medical_history.PatientID)
        new_diagnosis_id = update_data.get("MedicalDiagnosisID", db_medical_history.MedicalDiagnosisID)

        if "PatientID" in update_data or "MedicalDiagnosisID" in update_data:
            existing = db.query(PatientMedicalHistory).filter(
                PatientMedicalHistory.PatientID == new_patient_id,
                PatientMedicalHistory.MedicalDiagnosisID == new_diagnosis_id,
                PatientMedicalHistory.IsDeleted == "0",
                PatientMedicalHistory.Id != history_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="This patient already has a medical history record for this diagnosis"
                )

        for key, value in medical_history.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(db_medical_history, key, value)

        db_medical_history.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_medical_history)

        # Fetch patient and new diagnosis names
        patient = db.query(Patient).filter(
            Patient.id == db_medical_history.PatientID
        ).first()
        patient_name = patient.name if patient else None

        new_diagnosis = db.query(PatientMedicalDiagnosisList).filter(
            PatientMedicalDiagnosisList.Id == db_medical_history.MedicalDiagnosisID
        ).first()
        new_diagnosis_name = new_diagnosis.DiagnosisName if new_diagnosis else None

        # Build change description
        if old_diagnosis_name != new_diagnosis_name:
            change_desc = f"changed diagnosis from {old_diagnosis_name} -> {new_diagnosis_name}"
        else:
            change_desc = "updated details"

        updated_data_dict = serialize_data(medical_history.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=user_id,
            user_full_name=user_full_name,
            message=f"Updated medical history: {new_diagnosis_name} for {patient_name} ({change_desc})",
            table="PatientMedicalHistory",
            entity_id=history_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            patient_id = db_medical_history.PatientID,
            patient_full_name = patient_name,
            log_type="medical_history",
            is_system_config=False,
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

        # Fetch names before deletion
        patient = db.query(Patient).filter(
            Patient.id == db_medical_history.PatientID
        ).first()
        patient_name = patient.name if patient else None

        diagnosis = db.query(PatientMedicalDiagnosisList).filter(
            PatientMedicalDiagnosisList.Id == db_medical_history.MedicalDiagnosisID
        ).first()
        diagnosis_name = diagnosis.DiagnosisName if diagnosis else None

        db_medical_history.IsDeleted = '1'
        db_medical_history.ModifiedDate = datetime.now()
        db.commit()
        db.refresh(db_medical_history)

        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message=f"Deleted medical history: {diagnosis_name} for {patient_name}",
            table="PatientMedicalHistory",
            entity_id=history_id,
            original_data=original_data_dict,
            updated_data=None,
            patient_id = db_medical_history.PatientID,
            patient_full_name = patient_name,
            log_type="medical_history",
            is_system_config=False,
        )

    return db_medical_history