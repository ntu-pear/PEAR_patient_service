from sqlalchemy.orm import Session
from sqlalchemy import func, text
import cloudinary.uploader
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
import math
from fastapi import HTTPException, UploadFile
from typing import Optional, Dict, Any
import logging
from ..services.outbox_service import get_outbox_service, generate_correlation_id

logger = logging.getLogger(__name__)

def upload_photo_to_cloudinary(file: UploadFile):
    """ Upload photo to Cloudinary and return the URL """
    try:
        upload_result = cloudinary.uploader.upload(file.file)
        return upload_result["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")


def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
    if db_patient and mask:
        db_patient.nric = db_patient.mask_nric
    return db_patient


def get_patients(db: Session, mask: bool = True, pageNo: int = 0, pageSize: int = 10,name: Optional[str] = None,isActive: Optional[str] = None):
    offset = pageNo * pageSize
    query = db.query(Patient).filter(Patient.isDeleted == "0")

    # Apply name filter if provided (non-exact, case-insensitive match)
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))

    # Apply exact match for isActive (only accepts "0" or "1")
    if isActive in ["0", "1"]:
        query = query.filter(Patient.isActive == isActive)

    totalRecords = (
        db.query(func.count())
        .select_from(Patient)
        .filter(Patient.isDeleted == "0")
        .scalar()
    )
    totalPages = math.ceil(totalRecords / pageSize)

    db_patients = query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()

    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    return db_patients, totalRecords, totalPages


def _patient_to_dict(patient) -> Dict[str, Any]:
    """Convert patient model to dictionary for messaging"""
    try:
        if hasattr(patient, '__dict__'):
            patient_dict = {}
            for key, value in patient.__dict__.items():
                if not key.startswith('_'):
                    # Convert datetime objects to ISO format strings
                    if hasattr(value, 'isoformat'):
                        patient_dict[key] = value.isoformat()
                    else:
                        patient_dict[key] = value
            return patient_dict
        else:
            return {}
    except Exception as e:
        logger.error(f"Error converting patient to dict: {str(e)}")
        return {}

def create_patient(db: Session, patient: PatientCreate, user: str, user_full_name: str, correlation_id: str = None):
    """ Create a new patient with message queue publishing """

    # Check NRIC uniqueness
    existing_patient = (
        db.query(Patient)
        .filter(Patient.nric == patient.nric, Patient.isDeleted == "0")
        .first()
    )
    if existing_patient:
        raise HTTPException(status_code=400, detail="NRIC must be unique for active records")

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    try:
        # 1. Create patient object
        timestamp = datetime.now()

        # 2. Insert patient data
        query = text("""
            INSERT INTO [PATIENT] (
                name, nric, address, [tempAddress], [homeNo], [handphoneNo], gender, 
                [dateOfBirth], [isApproved], [preferredName], [preferredLanguageId], [updateBit], 
                [autoGame], [startDate], [endDate], [isActive], [isRespiteCare], [privacyLevel], 
                [terminationReason], [inActiveReason], [inActiveDate], [profilePicture], [createdDate], 
                [modifiedDate], [CreatedById], [ModifiedById], [isDeleted]
            ) VALUES (
                :name, :nric, :address, :tempAddress, :homeNo, :handphoneNo, :gender, 
                :dateOfBirth, :isApproved, :preferredName, :preferredLanguageId, :updateBit, 
                :autoGame, :startDate, :endDate, :isActive, :isRespiteCare, :privacyLevel, 
                :terminationReason, :inActiveReason, :inActiveDate, :profilePicture, :createdDate, 
                :modifiedDate, :CreatedById, :ModifiedById, :isDeleted
            );
        """)

        params = {
            "name": patient.name,
            "nric": patient.nric,
            "address": patient.address,
            "tempAddress": patient.tempAddress,
            "homeNo": patient.homeNo,
            "handphoneNo": patient.handphoneNo,
            "gender": patient.gender,
            "dateOfBirth": patient.dateOfBirth,
            "isApproved": patient.isApproved,
            "preferredName": patient.preferredName,
            "preferredLanguageId": patient.preferredLanguageId,
            "updateBit": patient.updateBit,
            "autoGame": patient.autoGame,
            "startDate": patient.startDate,
            "endDate": patient.endDate,
            "isActive": patient.isActive,
            "isRespiteCare": patient.isRespiteCare,
            "privacyLevel": patient.privacyLevel,
            "terminationReason": patient.terminationReason,
            "inActiveReason": patient.inActiveReason,
            "inActiveDate": patient.inActiveDate,
            "profilePicture": patient.profilePicture,
            "createdDate": timestamp,
            "modifiedDate": timestamp,
            "CreatedById": user,
            "ModifiedById": user,
            "isDeleted": patient.isDeleted,
        }

        db.execute(query, params)
        db.flush()

        # 3. Get the newly created patient
        new_patient = db.query(Patient).filter(Patient.nric == patient.nric).first()

        # 4. Create outbox event in the same transaction
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_CREATED',
            'patient_id': new_patient.id,
            'patient_data': _patient_to_dict(new_patient),
            'created_by': user,
            'created_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_CREATED',
            aggregate_id=new_patient.id,
            payload=event_payload,
            routing_key=f"patient.created.{new_patient.id}",
            correlation_id=correlation_id,
            created_by=user
        )

        # 5. Log the action
        patient_data_dict = {
            k: serialize_data(v)
            for k, v in new_patient.__dict__.items()
            if not k.startswith("_")
        }

        log_crud_action(
            action=ActionType.CREATE,
            user=user,
            user_full_name=user_full_name,
            message="Created Patient",
            table="Patient",
            entity_id=new_patient.id,
            original_data=None,
            updated_data=patient_data_dict,
        )

        # 6. Commit both patient and outbox event atomically
        db.commit()
        
        logger.info(f"Created patient {new_patient.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return new_patient

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")


def update_patient(db: Session, patient_id: int, patient: PatientUpdate, user: str, user_full_name: str, correlation_id: str = None):
    """Update patient with message queue publishing"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == "0").first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    try:
        # 1. Capture original data
        original_patient_dict = _patient_to_dict(db_patient)
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }

        # 2. Check NRIC uniqueness
        existing_patient = (
            db.query(Patient)
            .filter(
                Patient.id != patient_id,
                Patient.nric == patient.nric,
                Patient.isDeleted == "0",
            )
            .first()
        )
        if existing_patient:
            raise HTTPException(status_code=400, detail="NRIC must be unique for active records")

        # 3. Track BUSINESS LOGIC changes only (exclude audit fields)
        changes = {}
        patient_update_dict = patient.model_dump(exclude_unset=True)
        
        # Define audit fields to exclude from change tracking
        audit_fields = {'createdDate', 'modifiedDate', 'CreatedById', 'ModifiedById'}
        
        for key, new_value in patient_update_dict.items():
            if key not in audit_fields and hasattr(db_patient, key):
                old_value = getattr(db_patient, key)
                
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
                    
        # 4. Only proceed with update if there are actual business changes
        if changes:
            # Create consistent timestamp for all audit fields
            timestamp = datetime.now()

            # Apply business field updates
            for key, value in patient_update_dict.items():
                if key not in audit_fields:
                    setattr(db_patient, key, value)
            
            # Update audit fields
            db_patient.modifiedDate = timestamp
            db_patient.ModifiedById = user

            db.flush()

            # 5. Create outbox event only if there were changes
            outbox_service = get_outbox_service()
            
            event_payload = {
                'event_type': 'PATIENT_UPDATED',
                'patient_id': db_patient.id,
                'old_data': original_patient_dict,
                'new_data': _patient_to_dict(db_patient),
                'changes': changes,  # Only includes business field changes
                'modified_by': user,
                'modified_by_name': user_full_name,
                'timestamp': timestamp.isoformat(),  # Use same timestamp as db_patient.modifiedDate
                'correlation_id': correlation_id
            }
            
            outbox_event = outbox_service.create_event(
                db=db,
                event_type='PATIENT_UPDATED',
                aggregate_id=db_patient.id,
                payload=event_payload,
                routing_key=f"patient.updated.{db_patient.id}",
                correlation_id=correlation_id,
                created_by=user
            )

            # 6. Log the action
            log_crud_action(
                action=ActionType.UPDATE,
                user=user,
                user_full_name=user_full_name,
                message="Updated Patient",
                table="Patient",
                entity_id=db_patient.id,
                original_data=original_data_dict,
                updated_data=serialize_data(patient_update_dict),
            )

            # 7. Commit atomically
            db.commit()
            
            logger.info(f"Updated patient {db_patient.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        else:
            logger.info(f"Updated patient {db_patient.id} with no changes")

        return db_patient

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update patient: {str(e)}")


def update_patient_profile_picture(db: Session, patient_id: int, file: UploadFile, user_id: str, user_full_name: str):
    """ Update only the patient's profile picture """
    db_patient = db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == "0").first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    # Upload new profile picture to Cloudinary
    profile_picture_url = upload_photo_to_cloudinary(file)

    # Update patient profile picture
    db_patient.profilePicture = profile_picture_url
    db_patient.modifiedDate = datetime.now()
    db_patient.ModifiedById = user_id
    db.commit()
    db.refresh(db_patient)

    try:
        updated_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        updated_data_dict = "{}"
    log_crud_action(
        action=ActionType.UPDATE,
        user=user_id,
        user_full_name=user_full_name,
        message="Updated Patient Photo",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    return db_patient


def delete_patient(db: Session, patient_id: int, user_id: str, user_full_name: str, correlation_id: str = None):
    """Soft delete patient with message queue publishing"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = generate_correlation_id()

    try:
        # 1. Capture original data
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
        patient_dict = _patient_to_dict(db_patient)

        # 2. Perform soft delete
        timestamp = datetime.now()
        setattr(db_patient, "isDeleted", "1")
        db_patient.modifiedDate = timestamp
        db_patient.ModifiedById = user_id
        db.flush()

        # 3. Create outbox event
        outbox_service = get_outbox_service()
        
        event_payload = {
            'event_type': 'PATIENT_DELETED',
            'patient_id': db_patient.id,
            'patient_data': patient_dict,
            'deleted_by': user_id,
            'deleted_by_name': user_full_name,
            'timestamp': timestamp.isoformat(),
            'correlation_id': correlation_id
        }
        
        outbox_event = outbox_service.create_event(
            db=db,
            event_type='PATIENT_DELETED',
            aggregate_id=db_patient.id,
            payload=event_payload,
            routing_key=f"patient.deleted.{db_patient.id}",
            correlation_id=correlation_id,
            created_by=user_id
        )

        # 4. Log the action
        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message="Deleted Patient",
            table="Patient",
            entity_id=db_patient.id,
            original_data=original_data_dict,
            updated_data=None,
        )

        # 5. Commit atomically
        db.commit()
        
        logger.info(f"Deleted patient {db_patient.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return db_patient

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete patient: {str(e)}")

def delete_patient_profile_picture(db: Session, patient_id: int, user_id: str, user_full_name: str):
    """ Remove the patient's profile picture by setting it to an empty string """
    db_patient = db.query(Patient).filter(Patient.id == patient_id, Patient.isDeleted == "0").first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        original_data_dict = "{}"

    # Set profile picture to empty string
    db_patient.profilePicture = ""
    db_patient.modifiedDate = datetime.now()
    db_patient.ModifiedById = user_id
    db.commit()
    db.refresh(db_patient)

    try:
        updated_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        updated_data_dict = "{}"

    log_crud_action(
        action=ActionType.UPDATE,
        user=user_id,
        user_full_name=user_full_name,
        message="Deleted Patient Photo",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    return db_patient
