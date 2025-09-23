from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_medication_model import PatientMedication
from ..schemas.patient_medication import (
    PatientMedicationCreate,
    PatientMedicationUpdate
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
import math
from fastapi import HTTPException

# Get all medications (paginated)
def get_medications(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientMedication).filter(PatientMedication.IsDeleted == '0')
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_medications = (
        query.order_by(PatientMedication.Id.desc())
             .offset(offset)
             .limit(pageSize)
             .all()
    )
    return db_medications, totalRecords, totalPages

# Get all medications (paginated) for a specific patient
def get_patient_medications(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100):
    offset = pageNo * pageSize
    query = db.query(PatientMedication).filter(
        PatientMedication.PatientId == patient_id,
        PatientMedication.IsDeleted == '0'
    )
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    db_medications = (
        query.order_by(PatientMedication.Id.desc()) 
             .offset(offset)
             .limit(pageSize)
             .all()
    )
    return db_medications, totalRecords, totalPages

# Get a single medication by ID
def get_medication(db: Session, medication_id: int):
    return db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

# Create a new medication
def create_medication(
    db: Session,
    medication_data: PatientMedicationCreate,
    created_by: str,
    user_full_name: str
):
    """
    Creates a new PatientMedication record, sets CreatedDateTime, 
    UpdatedDateTime, CreatedById, and ModifiedById.
    """
    try:
        # Exclude any fields you set manually (like CreatedDateTime, etc.)
        data_dict = medication_data.model_dump(
            exclude={"CreatedDateTime", "UpdatedDateTime", "CreatedById", "ModifiedById"}
        )

        new_medication = PatientMedication(
            **data_dict,
            CreatedDateTime=datetime.utcnow(),
            UpdatedDateTime=datetime.utcnow(),
            CreatedById=created_by,
            ModifiedById=created_by,
            # IsDeleted="0"  # Mark as active
        )

        updated_data_dict = serialize_data(medication_data.model_dump())
        db.add(new_medication)
        db.commit()
        db.refresh(new_medication)

        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created medication record",
            table="PatientMedication",
            entity_id=new_medication.Id,
            original_data=None,
            updated_data=updated_data_dict,
        )
        return new_medication

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Update an existing medication
def update_medication(
    db: Session,
    medication_id: int,
    medication_data: PatientMedicationUpdate,
    modified_by: str,
    user_full_name: str
):
    """
    Updates a PatientMedication record by ID. Sets UpdatedDateTime and 
    ModifiedById. Returns the updated record.
    """
    db_medication = db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

    if not db_medication:
        return None  # or raise HTTPException(404, ...)

    try:
        # Serialize original data for logging
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    # Apply updates, excluding fields not set or that you handle manually
    update_fields = medication_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_medication, key, value)

    # Update metadata
    db_medication.UpdatedDateTime = datetime.utcnow()
    db_medication.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_medication)

        updated_data_dict = serialize_data(update_fields)
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated medication record",
            table="PatientMedication",
            entity_id=db_medication.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        return db_medication
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Soft delete a medication
def delete_medication(
    db: Session,
    medication_id: int,
    modified_by: str,
    user_full_name: str
):
    """
    Marks a PatientMedication record as deleted (IsDeleted='1') and
    logs the deletion. Returns the updated record.
    """
    db_medication = db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

    if not db_medication:
        return None  # or raise HTTPException(404, ...)

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    db_medication.IsDeleted = "1"
    db_medication.UpdatedDateTime = datetime.utcnow()
    db_medication.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_medication)

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Soft deleted medication record",
            table="PatientMedication",
            entity_id=db_medication.Id,
            original_data=original_data_dict,
            updated_data=serialize_data(db_medication),
        )
        return db_medication
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
