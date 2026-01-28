import logging
import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.patient_highlight_model import PatientHighlight
from app.services.highlight_helper import create_highlight_if_needed

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import (
    PatientPrescriptionCreate,
    PatientPrescriptionUpdate,
)

logger = logging.getLogger(__name__)

# Get all prescriptions (paginated)
def get_prescriptions(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientPrescription).filter(PatientPrescription.IsDeleted == '0')
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
def get_patient_prescriptions(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100):
    offset = pageNo * pageSize
    query = db.query(PatientPrescription).filter(
        PatientPrescription.PatientId == patient_id,
        PatientPrescription.IsDeleted == '0'
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
    return db.query(PatientPrescription).filter(
        PatientPrescription.Id == prescription_id,
        PatientPrescription.IsDeleted == '0'
    ).first()

# Create a new prescription
def create_prescription(
    db: Session,
    prescription_data: PatientPrescriptionCreate,
    created_by: str,
    user_full_name: str
):
    """
    Creates a new PatientPrescription record, sets CreatedDateTime, 
    ModifiedDateTime, CreatedById, and ModifiedById.
    """
    # Check for duplicate prescription
    existing_prescription = db.query(PatientPrescription).filter(
        PatientPrescription.PatientId == prescription_data.PatientId,
        PatientPrescription.PrescriptionListId == prescription_data.PrescriptionListId,
        PatientPrescription.IsDeleted == '0').first()
    
    if existing_prescription:
        raise HTTPException(status_code=400, detail="Duplicate prescription for the same patient and prescription list.")
    
    try:
        
        
        # Exclude any fields you set manually (like CreatedDateTime, etc.)
        data_dict = prescription_data.model_dump(
            exclude={"CreatedDateTime", "UpdatedDateTime", "CreatedById", "ModifiedById"}
        )

        new_prescription = PatientPrescription(
            **data_dict,
            CreatedDateTime=datetime.now(),
            UpdatedDateTime=datetime.now(),
            CreatedById=created_by,
            ModifiedById=created_by,
            # IsDeleted="0"  # Mark as active
        )

        updated_data_dict = serialize_data(prescription_data.model_dump())
        db.add(new_prescription)
        db.commit()
        db.refresh(new_prescription)

        prescription_with_details = db.query(PatientPrescription).options(
        joinedload(PatientPrescription.prescription_list)
        ).filter(
            PatientPrescription.Id == new_prescription.Id
        ).first()
        
        if prescription_with_details:
            try:
                create_highlight_if_needed(
                db=db,
                source_record=prescription_with_details,  # Has prescription_list loaded
                type_code="PRESCRIPTION",
                patient_id=new_prescription.PatientId,
                source_table="PATIENT_PRESCRIPTION",
                source_record_id=new_prescription.Id,
                created_by=created_by
                )
            except Exception as e:
                logger.error(f"Failed to create highlight for prescription {new_prescription.Id}: {e}")

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
    user_full_name: str
):
    """
    Updates a PatientPrescription record by ID. Sets ModifiedDateTime and 
    ModifiedById. Returns the updated record.
    """
    db_prescription = db.query(PatientPrescription).filter(
        PatientPrescription.Id == prescription_id,
        PatientPrescription.IsDeleted == '0'
    ).first()

    if not db_prescription:
        return None  # or raise HTTPException(404, ...)

    try:
        # Serialize original data for logging
        original_data_dict = {
            k: serialize_data(v) for k, v in db_prescription.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    # Apply updates, excluding fields not set or that you handle manually
    update_fields = prescription_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_prescription, key, value)

    # Update metadata
    db_prescription.ModifiedDateTime = datetime.now()
    db_prescription.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_prescription)

        # Highlight Integration
        prescription_with_details = db.query(PatientPrescription).options(
            joinedload(PatientPrescription.prescription_list)
        ).filter(
            PatientPrescription.Id == prescription_id
        ).first()
        
        if prescription_with_details:
            try:
                create_highlight_if_needed(
                    db=db,
                    source_record=prescription_with_details,  # Has prescription_list loaded
                    type_code="PRESCRIPTION",
                    patient_id=db_prescription.PatientId,
                    source_table="PATIENT_PRESCRIPTION",
                    source_record_id=prescription_id,
                    created_by=modified_by
                )
            except Exception as e:
                logger.error(f"Failed to create/update highlight for prescription {prescription_id}: {e}")

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
        return db_prescription
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Soft delete a prescription
def delete_prescription(
    db: Session,
    prescription_id: int,
    modified_by: str,
    user_full_name: str
):
    """
    Marks a PatientPrescription record as deleted (IsDeleted='1') and
    logs the deletion. Returns the updated record.
    """
    db_prescription = db.query(PatientPrescription).filter(
        PatientPrescription.Id == prescription_id,
        PatientPrescription.IsDeleted == '0'
    ).first()

    if not db_prescription:
        return None  # or raise HTTPException(404, ...)

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_prescription.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    db_prescription.IsDeleted = "1"
    db_prescription.ModifiedDateTime = datetime.now()
    db_prescription.ModifiedById = modified_by

    try:
        db.commit()
        
        try:
            highlights = db.query(PatientHighlight).filter(
                PatientHighlight.SourceTable == "PATIENT_PRESCRIPTION",
                PatientHighlight.SourceRecordId == prescription_id,
                PatientHighlight.IsDeleted == 0
            ).all()
            
            for highlight in highlights:
                highlight.IsDeleted = 1
                highlight.ModifiedDate = datetime.now()
                highlight.ModifiedById = modified_by
            
            if highlights:
                logger.info(f"Deleted {len(highlights)} highlights for prescription {prescription_id}")
            
            db.commit()
        except Exception as e:
            logger.error(f"Failed to delete highlights for prescription {prescription_id}: {e}")
        
        
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
        return db_prescription
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
