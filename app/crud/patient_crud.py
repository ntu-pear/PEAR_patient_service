import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional

import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from sqlalchemy import func, text
from sqlalchemy.orm import Session, joinedload

from app.models.patient_allocation_model import PatientAllocation

from ..crud import patient_guardian_crud as crud_guardian
from ..crud import patient_guardian_relationship_mapping_crud as crud_relationship
from ..crud import patient_patient_guardian_crud as crud_patient_patient_guardian
from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientCreateWithAllocation, PatientUpdate
from ..schemas.patient_guardian import PatientGuardianCreate
from ..schemas.patient_patient_guardian import PatientPatientGuardianCreate
from ..services.user_service import get_least_loaded_staff
from ..services.outbox_service import generate_correlation_id, get_outbox_service

logger = logging.getLogger(__name__)

MAX_PATIENTS_PER_GUARDIAN = 2

def upload_photo_to_cloudinary(file: UploadFile):
    """ Upload photo to Cloudinary and return the URL """
    try:
        upload_result = cloudinary.uploader.upload(file.file)
        return upload_result["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")

def get_patients_by_doctor(
    db: Session, 
    doctor_id: str, 
    mask: bool = True, 
    pageNo: int = 0, 
    pageSize: int = 10,
    name: Optional[str] = None,
    isActive: Optional[str] = None
):
    """Get all patients allocated to a specific doctor by doctorId (found in Patient Allocation table)"""
    offset = pageNo * pageSize
    
    # Query patients through the allocation relationship
    query = db.query(Patient).options(
        joinedload(Patient._preferred_language)
    ).join(
        PatientAllocation,
        Patient.id == PatientAllocation.patientId
    ).filter(
        PatientAllocation.doctorId == doctor_id,
        PatientAllocation.active == "Y",
        PatientAllocation.isDeleted == "0",
        Patient.isDeleted == "0"
    )
    
    # Apply name filter if provided (non-exact, case-insensitive match)
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    
    if isActive in ["0", "1"]:
        query = query.filter(Patient.isActive == isActive)
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    db_patients = query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()
    
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    
    return db_patients, totalRecords, totalPages


def get_patients_by_supervisor(
    db: Session, 
    supervisor_id: str, 
    mask: bool = True, 
    pageNo: int = 0, 
    pageSize: int = 10,
    name: Optional[str] = None,
    isActive: Optional[str] = None
):
    """Get all patients allocated to a specific supervisor by supervisorId (found in Patient Allocation table)"""
    offset = pageNo * pageSize
    
    # Query patients through the allocation relationship
    query = db.query(Patient).options(
        joinedload(Patient._preferred_language)
    ).join(
        PatientAllocation,
        Patient.id == PatientAllocation.patientId
    ).filter(
        PatientAllocation.supervisorId == supervisor_id,
        PatientAllocation.active == "Y",
        PatientAllocation.isDeleted == "0",
        Patient.isDeleted == "0"
    )
    
    # Apply name filter if provided (non-exact, case-insensitive match)
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    
    if isActive in ["0", "1"]:
        query = query.filter(Patient.isActive == isActive)
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    db_patients = query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()
    
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    
    return db_patients, totalRecords, totalPages


def get_patients_by_caregiver(
    db: Session, 
    caregiver_id: str, 
    mask: bool = True, 
    pageNo: int = 0, 
    pageSize: int = 10,
    name: Optional[str] = None,
    isActive: Optional[str] = None
):
    """Get all patients allocated to a specific caregiver by caregiverId (found in PatientAllocation table)"""
    offset = pageNo * pageSize
    
    # Query patients through the allocation relationship
    query = db.query(Patient).options(
        joinedload(Patient._preferred_language)
    ).join(
        PatientAllocation,
        Patient.id == PatientAllocation.patientId
    ).filter(
        PatientAllocation.caregiverId == caregiver_id,
        PatientAllocation.active == "Y",
        PatientAllocation.isDeleted == "0",
        Patient.isDeleted == "0"
    )
    
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    
    # Apply exact match for isActive (only accepts "0" or "1")
    if isActive in ["0", "1"]:
        query = query.filter(Patient.isActive == isActive)
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    db_patients = query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()
    
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    
    return db_patients, totalRecords, totalPages


def get_patients_by_guardian(
    db: Session, 
    guardian_application_user_id: str, 
    mask: bool = True, 
    pageNo: int = 0, 
    pageSize: int = 10,
    name: Optional[str] = None,
    isActive: Optional[str] = None
):
    """Get all patients allocated to a specific guardian by guardianApplicationUserId (found in Patient Guardian table)"""
    from ..models.patient_guardian_model import PatientGuardian
    
    offset = pageNo * pageSize
    
    # Query patients through the allocation and guardian relationships
    # Need to check both guardianId and guardian2Id in PatientAllocation
    query = db.query(Patient).options(
        joinedload(Patient._preferred_language)
    ).join(
        PatientAllocation,
        Patient.id == PatientAllocation.patientId
    ).join(
        PatientGuardian,
        (PatientAllocation.guardianId == PatientGuardian.id) | (PatientAllocation.guardian2Id == PatientGuardian.id)
    ).filter(
        PatientGuardian.guardianApplicationUserId == guardian_application_user_id,
        PatientAllocation.active == "Y",
        PatientAllocation.isDeleted == "0",
        PatientGuardian.isDeleted == "0",
        Patient.isDeleted == "0"
    )
    
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    
    if isActive in ["0", "1"]:
        query = query.filter(Patient.isActive == isActive)
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0
    
    db_patients = query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()
    
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    
    return db_patients, totalRecords, totalPages

def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = (
        db.query(Patient)
        .options(joinedload(Patient._preferred_language))
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
    if db_patient and mask:
        db_patient.nric = db_patient.mask_nric
    return db_patient

def get_patient_include_deleted(db: Session, patient_id: int, include_deleted: str, mask: bool = True):
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == include_deleted)
        .first()
    )
    if db_patient and mask:
        db_patient.nric = db_patient.mask_nric
    return db_patient


def get_patients(db: Session, mask: bool = True, pageNo: int = 0, pageSize: int = 10,name: Optional[str] = None,isActive: Optional[str] = None):
    offset = pageNo * pageSize
    query = db.query(Patient).options(joinedload(Patient._preferred_language)).filter(Patient.isDeleted == "0")

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
                    # Skip SQLAlchemy relationship objects - for language relationship object
                    if hasattr(value, '__tablename__'):
                        continue  # Skip this - it's a relationship object
                    # Convert datetime objects to ISO format strings
                    elif hasattr(value, 'isoformat'):
                        patient_dict[key] = value.isoformat()
                    else:
                        patient_dict[key] = value
            return patient_dict
        else:
            return {}
    except Exception as e:
        logger.error(f"Error converting patient to dict: {str(e)}")
        return {}

def create_patient(db: Session, patient: PatientCreateWithAllocation, user: str, user_full_name: str, correlation_id: str = None, api_key: str = None, supervisor_id: str = None):
    """ Create a new patient with message queue publishing """

    # Check NRIC uniqueness
    existing_patient = (
        db.query(Patient)
        .filter(Patient.nric == patient.nric, Patient.isDeleted == "0")
        .first()
    )
    if existing_patient:
        raise HTTPException(status_code=400, detail="NRIC must be unique for active records")

    # Reject if an active guardian already holds this NRIC
    from ..models.patient_guardian_model import PatientGuardian as PatientGuardianModel
    existing_guardian = (
        db.query(PatientGuardianModel)
        .filter(
            PatientGuardianModel.nric == patient.nric,
            PatientGuardianModel.isDeleted == "0",
            PatientGuardianModel.active == "Y",
        )
        .first()
    )
    if existing_guardian:
        raise HTTPException(
            status_code=400,
            detail="Patient NRIC conflicts with an existing active guardian record"
        )

    # Auto-assign (staff resolution + allocation) only applies to the allocation-aware schema
    has_allocation = isinstance(patient, PatientCreateWithAllocation)

    # Guardian for this patient can be an existing guardian (guardianId) or a brand-new one
    # created inline (newGuardian) - not both, and either requires a relationship name.
    guardian_id = getattr(patient, "guardianId", None)
    new_guardian_data = getattr(patient, "newGuardian", None)
    guardian_relationship_name = getattr(patient, "guardianRelationshipName", None)

    if guardian_id is not None and new_guardian_data is not None:
        raise HTTPException(status_code=400, detail="Provide either guardianId or newGuardian, not both")

    db_relationship_id = None
    if guardian_id is not None or new_guardian_data is not None:
        if not guardian_relationship_name:
            raise HTTPException(status_code=400, detail="guardianRelationshipName is required when linking a guardian")
        db_relationship_id = crud_relationship.get_relationshipId_by_relationshipName(db, guardian_relationship_name)
        if not db_relationship_id:
            raise HTTPException(status_code=404, detail="Relationship not found")

    if guardian_id is not None:
        guardian = (
            db.query(PatientGuardianModel)
            .filter(PatientGuardianModel.id == guardian_id, PatientGuardianModel.isDeleted == "0")
            .first()
        )
        if not guardian:
            raise HTTPException(status_code=400, detail="Guardian not found")

        active_patient_count = crud_patient_patient_guardian.count_active_patients_for_guardian(db, guardian_id)
        if active_patient_count >= MAX_PATIENTS_PER_GUARDIAN:
            raise HTTPException(
                status_code=400,
                detail=f"Guardian already has the maximum of {MAX_PATIENTS_PER_GUARDIAN} patients assigned"
            )

    # Validate doctor2Id != doctorId
    doctor_id = getattr(patient, "doctorId", None)
    doctor2_id = getattr(patient, "doctor2Id", None)
    if doctor2_id and doctor_id and doctor2_id == doctor_id:
        raise HTTPException(status_code=400, detail="doctor2Id must differ from doctorId")

    # Validate supervisor2Id != supervisorId
    supervisor2_id = getattr(patient, "supervisor2Id", None)
    if supervisor2_id and supervisor_id and supervisor2_id == supervisor_id:
        raise HTTPException(status_code=400, detail="supervisor2Id must differ from supervisorId")

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

        # 3. Get the newly created patient (filter isDeleted to avoid picking up a prior soft-deleted row with same NRIC)
        new_patient = db.query(Patient).filter(Patient.nric == patient.nric, Patient.isDeleted == "0").first()

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
            message=f"Created Patient: {new_patient.name}",
            table="Patient",
            entity_id=new_patient.id,
            original_data=None,
            updated_data=patient_data_dict,
            patient_id=new_patient.id,
            patient_full_name= new_patient.name,
            log_type= "patient_info",
        )

        # 6. Resolve care staff IDs (auto-assign does not depend on a guardian being set)
        if has_allocation:
            resolved_doctor_id = getattr(patient, "doctorId", None) or get_least_loaded_staff("DOCTOR", db, api_key)
            resolved_game_therapist_id = getattr(patient, "gameTherapistId", None) or get_least_loaded_staff("GAME THERAPIST", db, api_key)
            resolved_caregiver_id = getattr(patient, "caregiverId", None) or get_least_loaded_staff("CAREGIVER", db, api_key)

            doctor2_id = getattr(patient, "doctor2Id", None)
            if doctor2_id and doctor2_id == resolved_doctor_id:
                raise HTTPException(status_code=400, detail="doctor2Id must differ from doctorId")

        # 6a. Create a new guardian inline if requested, then link the guardian to this patient via
        # PATIENT_PATIENT_GUARDIAN (the source of truth for guardian assign/unassign/lookup)
        if has_allocation and new_guardian_data is not None:
            db_guardian = crud_guardian.create_guardian(
                db,
                PatientGuardianCreate(
                    **new_guardian_data.model_dump(),
                    patientId=new_patient.id,
                    relationshipName=guardian_relationship_name,
                    CreatedById=user,
                    ModifiedById=user,
                ),
                commit=False,
            )
            guardian_id = db_guardian.id

        if has_allocation and guardian_id is not None:
            crud_patient_patient_guardian.create_patient_patient_guardian(
                db,
                PatientPatientGuardianCreate(
                    guardianId=guardian_id,
                    patientId=new_patient.id,
                    relationshipId=db_relationship_id.id,
                    CreatedById=user,
                    ModifiedById=user,
                    isDeleted="0",
                ),
                commit=False,
            )

        # 7. Create allocation atomically (only when a guardian was given - PATIENT_ALLOCATION.guardianId is NOT NULL;
        # a patient created without one can have a guardian attached later via /Guardian/assign)
        if has_allocation and guardian_id is not None:
            db_allocation = PatientAllocation(
                active="Y",
                patientId=new_patient.id,
                guardianId=guardian_id,
                guardian2Id=None,
                doctorId=resolved_doctor_id,
                gameTherapistId=resolved_game_therapist_id,
                supervisorId=supervisor_id,
                caregiverId=resolved_caregiver_id,
                doctor2Id=getattr(patient, "doctor2Id", None),
                supervisor2Id=getattr(patient, "supervisor2Id", None),
                createdDate=timestamp,
                modifiedDate=timestamp,
                CreatedById=user,
                ModifiedById=user,
            )
            db.add(db_allocation)
            db.flush()

        # 8. Commit patient, outbox event, and allocation atomically
        db.commit()

        logger.info(f"Created patient {new_patient.id} with outbox event {outbox_event.id} (correlation: {correlation_id})")
        return new_patient

    except HTTPException:
        db.rollback()
        raise
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

        # Check NRIC doesn't conflict with an active guardian
        from ..models.patient_guardian_model import PatientGuardian as PatientGuardianModel
        existing_guardian = (
            db.query(PatientGuardianModel)
            .filter(
                PatientGuardianModel.nric == patient.nric,
                PatientGuardianModel.isDeleted == "0",
                PatientGuardianModel.active == "Y",
            )
            .first()
        )
        if existing_guardian:
            raise HTTPException(
                status_code=400,
                detail="Patient NRIC conflicts with an existing active guardian record"
            )

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
                message=f"Updated Patient: {db_patient.name}",
                table="Patient",
                entity_id=db_patient.id,
                original_data=original_data_dict,
                updated_data=serialize_data(patient_update_dict),
                patient_id=db_patient.id,
                patient_full_name= db_patient.name,
                log_type= "patient_info"
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
        message=f"Updated Patient Photo for patient : {db_patient.name}",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        patient_id=db_patient.id,
        patient_full_name= db_patient.name,
        log_type= "patient_info"
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
            message=f"Deleted Patient: {db_patient.name}",
            table="Patient",
            entity_id=db_patient.id,
            original_data=original_data_dict,
            updated_data=None,
            patient_id=db_patient.id,
            patient_full_name= db_patient.name,
            log_type= "patient_info"
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
        message=f"Deleted Patient Photo for patient: {db_patient.name}",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        patient_id=db_patient.id,
        patient_full_name= db_patient.name,
        log_type= "patient_info"
    )

    return db_patient
