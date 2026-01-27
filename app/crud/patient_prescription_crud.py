from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_prescription_model import PatientPrescription
from ..schemas.patient_prescription import (
    PatientPrescriptionCreate,
    PatientPrescriptionUpdate
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
import math
from fastapi import HTTPException

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

    #Look for existing record first
    db_prescription = db.query(PatientPrescription).filter(
            PatientPrescription.Id == prescription_id,
            PatientPrescription.IsDeleted == '0'
        ).first()

    if not db_prescription:
        return None
    
    #Look for matching patientId and prescription_list
    new_patient_id = prescription_data.PatientId or db_prescription.PatientId
    new_list_id = prescription_data.PrescriptionListId or db_prescription.PrescriptionListId

    duplicate_check = db.query(PatientPrescription).filter(
        PatientPrescription.PatientId == new_patient_id,
        PatientPrescription.PrescriptionListId == new_list_id,
        PatientPrescription.IsDeleted == '0',
        PatientPrescription.Id != prescription_id  
    ).first()

    if duplicate_check:
        raise HTTPException(
            status_code=400, 
            detail="Another prescription with this name already exists for this patient."
        )

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_prescription.__dict__.items() if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    update_fields = prescription_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_prescription, key, value)

    # Update metadata
    db_prescription.ModifiedDateTime = datetime.now()
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
