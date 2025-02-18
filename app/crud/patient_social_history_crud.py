from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.patient_model import (
    Patient,
)  # Ensure you import the Patient model correctly
from ..models.patient_social_history_model import PatientSocialHistory
from ..schemas.patient_social_history import (
    PatientSocialHistoryCreate,
    PatientSocialHistoryUpdate,
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

SYSTEM_USER_ID = "1"

# should it be based on the patientID or the socialID?


def get_social_history(db: Session, patient_id: int):
    return (
        db.query(PatientSocialHistory)
        .filter(PatientSocialHistory.patientId == patient_id)
        .first()
    )


def create_social_history(db: Session, social_history: PatientSocialHistoryCreate):
    # Check if the patientId exists in the PATIENT table
    patient = db.query(Patient).filter(Patient.id == social_history.patientId).first()

    if not patient:
        # If patient does not exist, raise an HTTP exception with a 400 status code
        raise HTTPException(
            status_code=400,
            detail=f"Patient with id {social_history.patientId} does not exist.",
        )

    # If patient exists, proceed with creating the social history record
    db_social_history = PatientSocialHistory(**social_history.model_dump())
    updated_data_dict = serialize_data(social_history.model_dump())
    db.add(db_social_history)
    db.commit()
    db.refresh(db_social_history)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        table="PatientSocialHistory",
        entity_id=db_social_history.id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_social_history


def update_social_history(
    db: Session, patient_id: int, social_history: PatientSocialHistoryUpdate
):
    """
    Update the social history record based on patientId.
    """
    db_social_history = (
        db.query(PatientSocialHistory)
        .filter(PatientSocialHistory.patientId == patient_id)
        .first()
    )
    if db_social_history:
        try:
            original_data_dict = {
                k: serialize_data(v)
                for k, v in db_social_history.__dict__.items()
                if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in social_history.model_dump().items():
            setattr(db_social_history, key, value)
        db.commit()
        db.refresh(db_social_history)

        updated_data_dict = serialize_data(social_history.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            table="PatientSocialHistory",
            entity_id=db_social_history.id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Social history record for patient with id {patient_id} not found.",
        )
    return db_social_history


def delete_social_history(db: Session, patient_id: int):
    """
    Perform a soft delete on the social history record based on patientId by changing 'IsDeleted' from '0' to '1'.
    """
    db_social_history = (
        db.query(PatientSocialHistory)
        .filter(PatientSocialHistory.patientId == patient_id)
        .first()
    )

    if db_social_history:
        try:
            original_data_dict = {
                k: serialize_data(v)
                for k, v in db_social_history.__dict__.items()
                if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        # Perform the soft delete by setting IsDeleted to '1'
        db_social_history.IsDeleted = "1"
        db.commit()
        db.refresh(db_social_history)

        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            table="PatientSocialHistory",
            entity_id=db_social_history.id,
            original_data=original_data_dict,
            updated_data=None,
        )
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Social history record for patient with id {patient_id} not found.",
        )

    return {
        "message": f"Social history record for patient with id {patient_id} has been soft deleted (marked inactive)."
    }
