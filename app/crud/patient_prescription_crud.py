import logging
import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data

# Import the messaging publisher
from ..messaging import get_patient_prescription_publisher

logger = logging.getLogger(__name__)

from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import (
    PatientPrescriptionCreate,
    PatientPrescriptionUpdate,
)


# Get all prescriptions (paginated)
def get_prescriptions(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientPrescription).filter(PatientPrescription.IsDeleted == "0")
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_prescriptions = (
        query.order_by(PatientPrescription.Id.desc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    return db_prescriptions, totalRecords, totalPages


# Get all prescriptions (paginated) for a specific patient
def get_patient_prescriptions(
    db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100
):
    offset = pageNo * pageSize
    query = db.query(PatientPrescription).filter(
        PatientPrescription.PatientId == patient_id,
        PatientPrescription.IsDeleted == "0",
    )
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_prescriptions = (
        query.order_by(PatientPrescription.Id.desc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    return db_prescriptions, totalRecords, totalPages


# Get a single prescription by ID
def get_prescription(db: Session, prescription_id: int):
    return (
        db.query(PatientPrescription)
        .filter(
            PatientPrescription.Id == prescription_id,
            PatientPrescription.IsDeleted == "0",
        )
        .first()
    )


# Create a new prescription
def create_prescription(
    db: Session,
    prescription_data: PatientPrescriptionCreate,
    created_by: str,
    user_full_name: str,
):
    """
    Creates a new PatientPrescription record, sets CreatedDateTime,
    ModifiedDateTime, CreatedById, and ModifiedById.
    """
    try:
        # Exclude any fields you set manually (like CreatedDateTime, etc.)
        data_dict = prescription_data.model_dump(
            exclude={
                "CreatedDateTime",
                "UpdatedDateTime",
                "CreatedById",
                "ModifiedById",
            }
        )

        new_prescription = PatientPrescription(
            **data_dict,
            CreatedDateTime=datetime.utcnow(),
            UpdatedDateTime=datetime.utcnow(),
            CreatedById=created_by,
            ModifiedById=created_by,
            # IsDeleted="0"  # Mark as active
        )

        updated_data_dict = serialize_data(prescription_data.model_dump())
        db.add(new_prescription)
        db.commit()
        db.refresh(new_prescription)

        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created prescription record",
            table="PatientPrescription",
            entity_id=new_prescription.Id,
            original_data=None,
            updated_data=updated_data_dict,
        )

        # Publish patient prescription creation event to message queue
        try:
            publisher = get_patient_prescription_publisher()
            # patient_dict = _patient_to_dict(new_patient)
            patient_prescription_dict = updated_data_dict
            success = publisher.publish_patient_prescription_created(
                patient_prescription_id=new_prescription.Id,
                patient_prescription_data=patient_prescription_dict,
                created_by=created_by
            )
            if not success:
                logger.warning(f"Failed to publish PATIENT_PRESCRIPTION_CREATED event for patient {new_prescription.Id}")
        except Exception as e:
            logger.error(f"Error publishing patient prescription creation event: {str(e)}")
            # Don't fail the operation if messaging fails

        return new_prescription

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Update an existing prescription
def update_prescription(
    db: Session,
    prescription_id: int,
    prescription_data: PatientPrescriptionUpdate,
    modified_by: str,
    user_full_name: str,
):
    """
    Updates a PatientPrescription record by ID. Sets ModifiedDateTime and
    ModifiedById. Returns the updated record.
    """
    db_prescription = (
        db.query(PatientPrescription)
        .filter(
            PatientPrescription.Id == prescription_id,
            PatientPrescription.IsDeleted == "0",
        )
        .first()
    )

    if not db_prescription:
        return None  # or raise HTTPException(404, ...)

    try:
        # Serialize original data for logging
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_prescription.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    # Apply updates, excluding fields not set or that you handle manually
    update_fields = prescription_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_prescription, key, value)

    # Update metadata
    db_prescription.ModifiedDateTime = datetime.utcnow()
    db_prescription.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_prescription)

        updated_data_dict = serialize_data(update_fields)
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated prescription record",
            table="PatientPrescription",
            entity_id=db_prescription.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        
        # Publish patient prescription update event to message queue
        try:
            publisher = get_patient_prescription_publisher()
            success = publisher.publish_patient_prescription_updated(
                patient_prescription_id=db_prescription.Id,
                old_data=original_data_dict,
                new_data=updated_data_dict,
                modified_by=modified_by
            )
            if not success:
                logger.warning(f"Failed to publish PATIENT_PRESCRIPTION_UPDATED event for patient {db_prescription.Id}")
        except Exception as e:
            logger.error(f"Error publishing patient prescription update event: {str(e)}")
            # Don't fail the operation if messaging fails
        
        return db_prescription
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Soft delete a prescription
def delete_prescription(
    db: Session, prescription_id: int, modified_by: str, user_full_name: str
):
    """
    Marks a PatientPrescription record as deleted (IsDeleted='1') and
    logs the deletion. Returns the updated record.
    """
    db_prescription = (
        db.query(PatientPrescription)
        .filter(
            PatientPrescription.Id == prescription_id,
            PatientPrescription.IsDeleted == "0",
        )
        .first()
    )

    if not db_prescription:
        return None  # or raise HTTPException(404, ...)

    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_prescription.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    db_prescription.IsDeleted = "1"
    db_prescription.ModifiedDateTime = datetime.utcnow()
    db_prescription.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_prescription)

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Soft deleted prescription record",
            table="PatientPrescription",
            entity_id=db_prescription.Id,
            original_data=original_data_dict,
            updated_data=serialize_data(db_prescription),
        )

         # Publish patient prescription update event to message queue
        try:
            publisher = get_patient_prescription_publisher()
            success = publisher.publish_patient_prescription_deleted(
                patient_prescription_id=db_prescription.Id,
                patient_prescription_data=original_data_dict,
                deleted_by=modified_by
            )
            if not success:
                logger.warning(f"Failed to publish PATIENT_PRESCRIPTION_DELETED event for patient {db_prescription.Id}")
        except Exception as e:
            logger.error(f"Error publishing patient prescription delete event: {str(e)}")
            # Don't fail the operation if messaging fails
        
        return db_prescription
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
