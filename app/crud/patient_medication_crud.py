from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_medication_model import PatientMedication
from ..schemas.patient_medication import (
    PatientMedicationCreate,
    PatientMedicationUpdate
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
from ..services.outbox_service import get_outbox_service, generate_correlation_id
import math
import logging
from fastapi import HTTPException
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def _medication_to_dict(medication) -> Dict[str, Any]:
    """Convert medication model to dictionary for messaging"""
    try:
        if hasattr(medication, '__dict__'):
            medication_dict = {}
            for key, value in medication.__dict__.items():
                if not key.startswith('_'):
                    # Convert datetime objects to ISO format strings
                    if hasattr(value, 'isoformat'):
                        medication_dict[key] = value.isoformat()
                    else:
                        medication_dict[key] = value
            return medication_dict
        else:
            return {}
    except Exception as e:
        logger.error(f"Error converting medication to dict: {str(e)}")
        return {}

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
    user_full_name: str,
    correlation_id: Optional[str] = None
):
    """
    Creates a new PatientMedication record with outbox pattern support.
    """
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    # 1. Create consistent timestamp for database and event
    timestamp = datetime.utcnow()

    try:
        # 2. Exclude any fields you set manually (like CreatedDateTime, etc.)
        data_dict = medication_data.model_dump(
            exclude={"CreatedDateTime", "UpdatedDateTime", "CreatedById", "ModifiedById", "IsDeleted"}
        )

        new_medication = PatientMedication(
            **data_dict,
            CreatedDateTime=timestamp,
            UpdatedDateTime=timestamp,
            CreatedById=created_by,
            ModifiedById=created_by,
            IsDeleted="0"  # Ensure it's set as active
        )

        db.add(new_medication)
        db.flush()  # Get ID without committing

        # 3. Create outbox event in the same transaction
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_CREATED',
            'medication_id': new_medication.Id,
            'patient_id': new_medication.PatientId,
            'medication_data': _medication_to_dict(new_medication),
            'created_by': created_by,
            'timestamp': timestamp.isoformat(),  # Use same timestamp
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_MEDICATION_CREATED',
            aggregate_id=new_medication.Id,
            payload=event_payload,
            routing_key=f"patient.medication.created.{new_medication.Id}",
            correlation_id=correlation_id,
            created_by=created_by
        )

        # 4. Log the action
        updated_data_dict = serialize_data(medication_data.model_dump())
        
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

        # 5. Commit both medication and outbox event atomically
        db.commit()
        db.refresh(new_medication)
        
        logger.info(f"Created medication {new_medication.Id} for patient {new_medication.PatientId} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return new_medication

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create medication: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create medication: {str(e)}")

# Update an existing medication
def update_medication(
    db: Session,
    medication_id: int,
    medication_data: PatientMedicationUpdate,
    modified_by: str,
    user_full_name: str,
    correlation_id: Optional[str] = None
):
    """
    Updates a PatientMedication record by ID with outbox pattern support.
    """
    db_medication = db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

    if not db_medication:
        return None  # Return None for backward compatibility with existing tests

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    try:
        # 1. Track business field changes only (exclude audit fields)
        changes = {}
        update_fields = medication_data.model_dump(exclude_unset=True)
        
        # Define audit fields to exclude from change tracking
        audit_fields = {'CreatedDateTime', 'UpdatedDateTime', 'CreatedById', 'ModifiedById'}
        
        for key, new_value in update_fields.items():
            if key not in audit_fields and hasattr(db_medication, key):
                old_value = getattr(db_medication, key)
                if old_value != new_value:
                    changes[key] = {
                        'old': serialize_data(old_value),
                        'new': serialize_data(new_value)
                    }

        # 2. Early return if no business changes detected
        if not changes:
            logger.info(f"No changes detected for medication {medication_id}, skipping update")
            return db_medication

        # 3. Create consistent timestamp for database and event
        timestamp = datetime.utcnow()

        # 4. Capture original data before changes (for logging and events)
        original_medication_dict = _medication_to_dict(db_medication)
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() 
            if not k.startswith("_")
        }

        # 5. Apply business field updates
        for key, value in update_fields.items():
            if key not in audit_fields:  # Only update non-audit fields
                setattr(db_medication, key, value)

        # 6. Update audit fields only when there are business changes
        db_medication.UpdatedDateTime = timestamp
        db_medication.ModifiedById = modified_by
        
        db.flush()

        # 7. Create outbox event (only reached if changes exist)
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_UPDATED',
            'medication_id': db_medication.Id,
            'patient_id': db_medication.PatientId,
            'old_data': original_medication_dict,
            'new_data': _medication_to_dict(db_medication),
            'changes': changes,  # Only contains business field changes
            'modified_by': modified_by,
            'timestamp': timestamp.isoformat(),  # Use same timestamp
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_MEDICATION_UPDATED',
            aggregate_id=db_medication.Id,
            payload=event_payload,
            routing_key=f"patient.medication.updated.{db_medication.Id}",
            correlation_id=correlation_id,
            created_by=modified_by
        )

        # 8. Log the action
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

        # 9. Commit atomically
        db.commit()
        db.refresh(db_medication)
        
        logger.info(f"Updated medication {db_medication.Id} for patient {db_medication.PatientId} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_medication

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update medication: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update medication: {str(e)}")

# Soft delete a medication
def delete_medication(
    db: Session,
    medication_id: int,
    modified_by: str,
    user_full_name: str,
    correlation_id: Optional[str] = None
):
    """
    Marks a PatientMedication record as deleted (IsDeleted='1') with outbox pattern support.
    """
    db_medication = db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

    if not db_medication:
        return None  # Return None for backward compatibility with existing tests

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    # Create consistent timestamp for database and event
    timestamp = datetime.utcnow()

    try:
        # 1. Capture original data
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() 
            if not k.startswith("_")
        }
        medication_dict = _medication_to_dict(db_medication)

        # 2. Perform soft delete
        db_medication.IsDeleted = "1"
        db_medication.UpdatedDateTime = timestamp
        db_medication.ModifiedById = modified_by
        
        db.flush()

        # 3. Create outbox event
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_DELETED',
            'medication_id': db_medication.Id,
            'patient_id': db_medication.PatientId,
            'medication_data': medication_dict,
            'deleted_by': modified_by,
            'timestamp': timestamp.isoformat(),  # Use same timestamp
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_MEDICATION_DELETED',
            aggregate_id=db_medication.Id,
            payload=event_payload,
            routing_key=f"patient.medication.deleted.{db_medication.Id}",
            correlation_id=correlation_id,
            created_by=modified_by
        )

        # 4. Log the action
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

        # 5. Commit atomically
        db.commit()
        db.refresh(db_medication)
        
        logger.info(f"Deleted medication {db_medication.Id} for patient {db_medication.PatientId} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_medication

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete medication: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete medication: {str(e)}")
