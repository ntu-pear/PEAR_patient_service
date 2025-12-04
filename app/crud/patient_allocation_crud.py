import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.patient_allocation_model import PatientAllocation
from ..models.patient_guardian_model import PatientGuardian
from ..schemas.patient_allocation import PatientAllocationCreate, PatientAllocationUpdate
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..services.outbox_service import generate_correlation_id, get_outbox_service

logger = logging.getLogger(__name__)

def _allocation_to_dict(allocation) -> Dict[str, Any]:
    """Convert allocation model to dictionary for messaging"""
    try:
        if hasattr(allocation, '__dict__'):
            allocation_dict = {}
            for key, value in allocation.__dict__.items():
                if not key.startswith('_'):
                    # Skip SQLAlchemy relationship objects
                    if hasattr(value, '__tablename__'):
                        continue
                    # Convert datetime objects to ISO format strings
                    elif hasattr(value, 'isoformat'):
                        allocation_dict[key] = value.isoformat()
                    else:
                        allocation_dict[key] = value
            return allocation_dict
        else:
            return {}
    except Exception as e:
        logger.error(f"Error converting allocation to dict: {str(e)}")
        return {}

def get_allocation_by_id(db: Session, allocation_id: int):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.id == allocation_id
        ).first()
        
        if not res: return None
        
        allocation, guardian_user_id = res
        data = allocation.__dict__.copy()
        data["guardianApplicationUserId"] = guardian_user_id
        data.pop('_sa_instance_state',None)
        return data
    
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_allocation_by_patient(db: Session, patient_id: int):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.patientId == patient_id,
            PatientAllocation.active == "Y"
        ).first()
        
        if not res: return None

        allocation, guardian_user_id = res
        data = allocation.__dict__.copy()
        data["guardianApplicationUserId"] = guardian_user_id
        data.pop('_sa_instance_state',None)
        return data
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_guardian_id_by_patient(db: Session, patient_id: int):
    try:
        res = db.query(PatientGuardian.guardianApplicationUserId).join(
            PatientAllocation, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.patientId == patient_id
        ).first()
        
        if not res: return None
        
        return res[0]
        
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_all_allocations(db: Session, skip: int = 0, limit: int = 100):
    try:
        res = db.query(PatientAllocation, PatientGuardian.guardianApplicationUserId).join(
            PatientGuardian, PatientAllocation.guardianId == PatientGuardian.id
        ).filter(
            PatientAllocation.active == "Y"
        ).order_by(
            PatientAllocation.id
        ).offset(
            skip
        ).limit(
            limit
        ).all()
        if not res: return None
        allocation_list = []
        
        for allocation, guardian_user_id in res:
            data = allocation.__dict__.copy()
            data["guardianApplicationUserId"] = guardian_user_id
            data.pop('_sa_instance_state',None)
            allocation_list.append(data)
            
        return allocation_list
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def create_allocation(db: Session, allocation: PatientAllocationCreate, user_id: str, user_full_name: str, correlation_id: str = None):
    """Create a new patient allocation with message queue publishing"""
    
    # Check if patient already has an active allocation
    existing = get_allocation_by_patient(db, allocation.patientId)
    if existing:
        raise ValueError("Patient already has an active allocation")
    
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    try:
        # 1. Create allocation object
        timestamp = datetime.now()
        
        db_allocation = PatientAllocation(
            active="Y",
            patientId=allocation.patientId,
            doctorId=allocation.doctorId,
            gameTherapistId=allocation.gameTherapistId,
            supervisorId=allocation.supervisorId,
            caregiverId=allocation.caregiverId,
            guardianId=allocation.guardianId,
            tempDoctorId=allocation.tempDoctorId,
            tempCaregiverId=allocation.tempCaregiverId,
            secondaryGuardianId=allocation.secondaryGuardianId,
            createdDate=timestamp,
            modifiedDate=timestamp,
            CreatedById=user_id,
            ModifiedById=user_id
        )
        db.add(db_allocation)
        db.flush()
        
        # 2. Create outbox event in the same transaction
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_ALLOCATION_CREATED',
            'allocation_id': db_allocation.id,
            'patient_id': db_allocation.patientId,
            'allocation_data': _allocation_to_dict(db_allocation),
            'created_by': user_id,
            'created_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_ALLOCATION_CREATED',
            aggregate_id=db_allocation.id,
            payload=event_payload,
            routing_key=f"patient.allocation.created.{db_allocation.id}",
            correlation_id=correlation_id,
            created_by=user_id
        )
        
        # 3. Log the action
        allocation_data_dict = {
            k: serialize_data(v)
            for k, v in db_allocation.__dict__.items()
            if not k.startswith("_")
        }
        
        log_crud_action(
            action=ActionType.CREATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Created Patient Allocation",
            table="PatientAllocation",
            entity_id=db_allocation.id,
            original_data=None,
            updated_data=allocation_data_dict,
        )
        
        # 4. Commit both allocation and outbox event atomically
        db.commit()
        db.refresh(db_allocation)
        
        logger.info(f"Created patient allocation {db_allocation.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_allocation
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create patient allocation: {str(e)}")
        raise e

def update_allocation(db: Session, allocation_id: int, allocation: PatientAllocationUpdate, user_id: str, user_full_name: str, correlation_id: str = None):
    """Update patient allocation with message queue publishing"""
    
    # Get the allocation as an object, not a dict
    db_allocation = db.query(PatientAllocation).filter(
        PatientAllocation.id == allocation_id
    ).first()
    
    if not db_allocation:
        return None
        
    if db_allocation.active != "Y":
        raise ValueError("Cannot update inactive allocation")
    
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    try:
        # 1. Capture original data
        original_allocation_dict = _allocation_to_dict(db_allocation)
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_allocation.__dict__.items()
            if not k.startswith("_")
        }
        
        # 2. Track BUSINESS LOGIC changes only (exclude audit fields)
        changes = {}
        allocation_update_dict = allocation.model_dump(exclude_unset=True)
        
        # Define audit fields to exclude from change tracking
        audit_fields = {'createdDate', 'modifiedDate', 'CreatedById', 'ModifiedById'}
        
        for key, new_value in allocation_update_dict.items():
            if key not in audit_fields and hasattr(db_allocation, key):
                old_value = getattr(db_allocation, key)
                
                # Strip timezone for datetime comparison
                if hasattr(old_value, 'replace') and hasattr(old_value, 'tzinfo') and old_value.tzinfo:
                    old_value = old_value.replace(tzinfo=None)
                if hasattr(new_value, 'replace') and hasattr(new_value, 'tzinfo') and new_value.tzinfo:
                    new_value = new_value.replace(tzinfo=None)
                
                if old_value != new_value:
                    changes[key] = {
                        'old': serialize_data(old_value),
                        'new': serialize_data(new_value)
                    }
        
        # 3. Only proceed with update if there are actual business changes
        if changes:
            # Create consistent timestamp for all audit fields
            timestamp = datetime.now()
            
            # Apply business field updates
            for key, value in allocation_update_dict.items():
                if key not in audit_fields:
                    setattr(db_allocation, key, value)
            
            # Update audit fields
            db_allocation.modifiedDate = timestamp
            db_allocation.ModifiedById = user_id
            
            db.flush()
            
            # 4. Create outbox event only if there were changes
            outbox_service = get_outbox_service()
            
            event_payload = {
                'event_type': 'PATIENT_ALLOCATION_UPDATED',
                'allocation_id': db_allocation.id,
                'patient_id': db_allocation.patientId,
                'old_data': original_allocation_dict,
                'new_data': _allocation_to_dict(db_allocation),
                'changes': changes,  # Only includes business field changes
                'modified_by': user_id,
                'modified_by_name': user_full_name,
                'timestamp': timestamp.isoformat(),
                'correlation_id': correlation_id
            }
            
            outbox_event = outbox_service.create_event(
                db=db,
                event_type='PATIENT_ALLOCATION_UPDATED',
                aggregate_id=db_allocation.id,
                payload=event_payload,
                routing_key=f"patient.allocation.updated.{db_allocation.id}",
                correlation_id=correlation_id,
                created_by=user_id
            )
            
            # 5. Log the action
            log_crud_action(
                action=ActionType.UPDATE,
                user=user_id,
                user_full_name=user_full_name,
                message="Updated Patient Allocation",
                table="PatientAllocation",
                entity_id=db_allocation.id,
                original_data=original_data_dict,
                updated_data=serialize_data(allocation_update_dict),
            )
            
            # 6. Commit atomically
            db.commit()
            db.refresh(db_allocation)
            
            logger.info(f"Updated patient allocation {db_allocation.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        else:
            logger.info(f"Updated patient allocation {db_allocation.id} with no changes")
        
        return db_allocation
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to update patient allocation: {str(e)}")
        raise e

def delete_allocation(db: Session, allocation_id: int, user_id: str, user_full_name: str, correlation_id: str = None):
    """Soft delete patient allocation with message queue publishing"""
    
    # Get the allocation as an object, not a dict
    db_allocation = db.query(PatientAllocation).filter(
        PatientAllocation.id == allocation_id
    ).first()
    
    if not db_allocation:
        return None
        
    if db_allocation.active != "Y":
        raise ValueError("Allocation is already inactive")
    
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    try:
        # 1. Capture original data
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_allocation.__dict__.items()
            if not k.startswith("_")
        }
        allocation_dict = _allocation_to_dict(db_allocation)
        
        # 2. Perform soft delete
        timestamp = datetime.now()
        db_allocation.isDeleted = "1"
        db_allocation.modifiedDate = timestamp
        db_allocation.ModifiedById = user_id
        db.flush()
        
        # 3. Create outbox event
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_ALLOCATION_DELETED',
            'allocation_id': db_allocation.id,
            'patient_id': db_allocation.patientId,
            'allocation_data': allocation_dict,
            'deleted_by': user_id,
            'deleted_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_ALLOCATION_DELETED',
            aggregate_id=db_allocation.id,
            payload=event_payload,
            routing_key=f"patient.allocation.deleted.{db_allocation.id}",
            correlation_id=correlation_id,
            created_by=user_id
        )
        
        # 4. Log the action
        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message="Deleted Patient Allocation",
            table="PatientAllocation",
            entity_id=db_allocation.id,
            original_data=original_data_dict,
            updated_data=None,
        )
        
        # 5. Commit atomically
        db.commit()
        
        logger.info(f"Deleted patient allocation {db_allocation.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_allocation
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to delete patient allocation: {str(e)}")
        raise e
    