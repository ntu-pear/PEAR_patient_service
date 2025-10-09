from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from ..models.patient_medication_model import PatientMedication
from ..models.patient_prescription_list_model import PatientPrescriptionList
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

def _get_prescription_name_by_id(db: Session, prescription_list_id: int) -> Optional[str]:
    """Get prescription name by ID - safe method that works with mocks"""
    try:
        prescription = db.query(PatientPrescriptionList).filter(
            PatientPrescriptionList.Id == prescription_list_id,
            PatientPrescriptionList.IsDeleted == '0'
        ).first()
        return prescription.Value if prescription else None
    except Exception as e:
        logger.warning(f"Could not fetch prescription name for ID {prescription_list_id}: {str(e)}")
        return None

def _medication_to_dict_with_prescription_name(medication, db: Optional[Session] = None) -> Dict[str, Any]:
    """Convert medication model to dictionary for messaging, including prescription name"""
    try:
        if hasattr(medication, '__dict__'):
            medication_dict = {}
            
            # Process all attributes, but exclude SQLAlchemy relationship objects
            for key, value in medication.__dict__.items():
                if not key.startswith('_') and not hasattr(value, '_sa_class_manager'):
                    # Convert datetime objects to ISO format strings
                    if hasattr(value, 'isoformat'):
                        medication_dict[key] = value.isoformat()
                    else:
                        medication_dict[key] = value
            
            # Try to get prescription name in multiple ways
            prescription_name = None
            
            # Method 1: From loaded relationship (production)
            if hasattr(medication, 'prescription_list') and medication.prescription_list:
                try:
                    if hasattr(medication.prescription_list, 'Value'):
                        prescription_name = medication.prescription_list.Value
                        logger.debug(f"Got prescription name from relationship: '{prescription_name}'")
                except Exception as e:
                    logger.debug(f"Could not get prescription name from relationship: {e}")
            
            # Method 2: Query by ID if we have database access (production fallback)
            if not prescription_name and db and hasattr(medication, 'PrescriptionListId'):
                prescription_list_id = getattr(medication, 'PrescriptionListId', None)
                if prescription_list_id:
                    prescription_name = _get_prescription_name_by_id(db, prescription_list_id)
                    if prescription_name:
                        logger.debug(f"Got prescription name by query: '{prescription_name}'")
            
            # Method 3: Check if it's already in the medication dict (from direct attribute setting in tests)
            if not prescription_name and 'PrescriptionName' in medication_dict:
                prescription_name = medication_dict['PrescriptionName']
                logger.debug(f"Got prescription name from medication dict: '{prescription_name}'")
                
            # Method 4: Mock object attribute (for tests)
            if not prescription_name and hasattr(medication, 'PrescriptionName'):
                prescription_name = getattr(medication, 'PrescriptionName', None)
                logger.debug(f"Got prescription name from mock attribute: '{prescription_name}'")
            
            # Always ensure PrescriptionName is in the dictionary
            medication_dict['PrescriptionName'] = prescription_name
            
            logger.debug(f"Final prescription name: '{prescription_name}'")
            return medication_dict
        else:
            logger.warning("Medication object has no __dict__ attribute")
            return {}
    except Exception as e:
        logger.error(f"Error converting medication to dict: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {}

def _medication_to_dict_with_explicit_prescription_name(db: Session, medication, prescription_list_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Convert medication model to dictionary for messaging, with explicit prescription name lookup.
    Use this when you need to ensure the prescription name matches a specific prescription_list_id.
    """
    try:
        if hasattr(medication, '__dict__'):
            medication_dict = {}
            
            # Process all attributes, but exclude SQLAlchemy relationship objects
            for key, value in medication.__dict__.items():
                if not key.startswith('_') and not hasattr(value, '_sa_class_manager'):
                    # Convert datetime objects to ISO format strings
                    if hasattr(value, 'isoformat'):
                        medication_dict[key] = value.isoformat()
                    else:
                        medication_dict[key] = value
            
            # Get prescription name - use provided prescription_list_id if given, otherwise use medication's current value
            target_prescription_id = prescription_list_id or medication_dict.get('PrescriptionListId')
            
            if target_prescription_id:
                prescription_name = _get_prescription_name_by_id(db, target_prescription_id)
                logger.debug(f"Fetched prescription name for ID {target_prescription_id}: '{prescription_name}'")
            else:
                prescription_name = None
                logger.warning("No PrescriptionListId available for prescription name lookup")
            
            # Always add PrescriptionName to the dictionary
            medication_dict['PrescriptionName'] = prescription_name
            
            return medication_dict
        else:
            logger.warning("Medication object has no __dict__ attribute")
            return {}
    except Exception as e:
        logger.error(f"Error converting medication to dict with explicit prescription name: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {}

def _get_medication_with_prescription_name(db: Session, medication_id: int):
    """Get medication with prescription name loaded - with error handling for tests"""
    try:
        return db.query(PatientMedication).options(
            joinedload(PatientMedication.prescription_list)
        ).filter(
            PatientMedication.Id == medication_id,
            PatientMedication.IsDeleted == '0'
        ).first()
    except Exception as e:
        # This might fail in tests with mocks - fall back to simple query
        logger.warning(f"Could not load medication with prescription relationship: {e}")
        return db.query(PatientMedication).filter(
            PatientMedication.Id == medication_id,
            PatientMedication.IsDeleted == '0'
        ).first()

def _medication_to_dict(medication) -> Dict[str, Any]:
    """Convert medication model to dictionary for messaging (legacy function)"""
    try:
        if hasattr(medication, '__dict__'):
            medication_dict = {}
            for key, value in medication.__dict__.items():
                if not key.startswith('_') and not hasattr(value, '_sa_class_manager'):
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

# Your existing get functions remain the same...
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

def get_medication(db: Session, medication_id: int):
    return db.query(PatientMedication).filter(
        PatientMedication.Id == medication_id,
        PatientMedication.IsDeleted == '0'
    ).first()

# Updated create_medication function
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

    # Create consistent timestamp for database and event
    timestamp = datetime.now()

    try:
        # Exclude any fields you set manually
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

        # Try to load with prescription relationship, but handle failures gracefully
        medication_with_prescription = _get_medication_with_prescription_name(db, new_medication.Id)
        
        if medication_with_prescription:
            logger.debug("Successfully loaded medication with prescription relationship")
            medication_for_event = medication_with_prescription
        else:
            logger.warning("Failed to load medication with prescription, using original")
            medication_for_event = new_medication

        # Create outbox event with the medication data (pass db session for prescription lookup)
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_CREATED',
            'medication_id': new_medication.Id,
            'patient_id': new_medication.PatientId,
            'medication_data': _medication_to_dict_with_prescription_name(medication_for_event, db),
            'created_by': created_by,
            'created_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
            'correlation_id': correlation_id
        }
        
        # Debug: Log the payload before sending
        logger.info(f"Event payload prescription name: '{event_payload['medication_data'].get('PrescriptionName')}'")
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_MEDICATION_CREATED',
            aggregate_id=new_medication.Id,
            payload=event_payload,
            routing_key=f"patient.medication.created.{new_medication.Id}",
            correlation_id=correlation_id,
            created_by=created_by
        )

        # Log the action
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

        # Commit both medication and outbox event atomically
        db.commit()
        db.refresh(new_medication)
        
        logger.info(f"Created medication {new_medication.Id} for patient {new_medication.PatientId} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return new_medication

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create medication: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create medication: {str(e)}")

# Updated update_medication function
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
        return None

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    try:
        # Track BUSINESS LOGIC changes only (exclude audit fields)
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

        # Early return if no business changes detected
        if not changes:
            logger.info(f"No changes detected for medication {medication_id}, skipping update")
            return db_medication

        # Create consistent timestamp for database and event
        timestamp = datetime.now()

        # Capture ORIGINAL prescription details
        original_prescription_list_id = db_medication.PrescriptionListId
        original_medication_dict = _medication_to_dict_with_explicit_prescription_name(
            db, db_medication, original_prescription_list_id
        )
        
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() 
            if not k.startswith("_")
        }

        # Apply business field updates only
        new_prescription_list_id = None
        for key, value in update_fields.items():
            if key not in audit_fields:
                setattr(db_medication, key, value)
                if key == 'PrescriptionListId':
                    new_prescription_list_id = value
                    logger.info(f"PrescriptionListId changing from {original_prescription_list_id} to {new_prescription_list_id}")

        # Update audit fields
        db_medication.UpdatedDateTime = timestamp
        db_medication.ModifiedById = modified_by
        
        db.flush()

        # Get the updated medication data with the CORRECT prescription name
        # Use the NEW prescription_list_id if it was changed, otherwise use current value
        target_prescription_id = new_prescription_list_id or db_medication.PrescriptionListId
        updated_medication_dict = _medication_to_dict_with_explicit_prescription_name(
            db, db_medication, target_prescription_id
        )

        # Debug logging
        logger.info(f"Original prescription ID: {original_prescription_list_id}, name: '{original_medication_dict.get('PrescriptionName')}'")
        logger.info(f"New prescription ID: {target_prescription_id}, name: '{updated_medication_dict.get('PrescriptionName')}'")

        # Create outbox event
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_UPDATED',
            'medication_id': db_medication.Id,
            'patient_id': db_medication.PatientId,
            'old_data': original_medication_dict,
            'new_data': updated_medication_dict,  # This now has the CORRECT prescription name
            'changes': changes,  # Only includes business field changes
            'modified_by': modified_by,
            'modified_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),  # Use same timestamp as db_medication.UpdatedDateTime
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

        # Log the action
        updated_data_dict = serialize_data({k: v for k, v in update_fields.items() if k not in audit_fields})
        
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

        # Commit atomically
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
        return None

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    # Create consistent timestamp for database and event
    timestamp = datetime.now()

    try:
        # Capture original data with prescription name
        medication_dict = _medication_to_dict_with_prescription_name(db_medication, db)
        
        original_data_dict = {
            k: serialize_data(v) for k, v in db_medication.__dict__.items() 
            if not k.startswith("_")
        }

        # Perform soft delete
        db_medication.IsDeleted = "1"
        db_medication.UpdatedDateTime = timestamp
        db_medication.ModifiedById = modified_by
        
        db.flush()

        # Create outbox event
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_MEDICATION_DELETED',
            'medication_id': db_medication.Id,
            'patient_id': db_medication.PatientId,
            'medication_data': medication_dict,
            'deleted_by': modified_by,
            'deleted_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
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

        # Log the action
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

        # Commit atomically
        db.commit()
        db.refresh(db_medication)
        
        logger.info(f"Deleted medication {db_medication.Id} for patient {db_medication.PatientId} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_medication

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete medication: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete medication: {str(e)}")
