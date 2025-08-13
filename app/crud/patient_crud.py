import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional

import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data

# Import the messaging publisher
from ..messaging import get_patient_publisher
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate

logger = logging.getLogger(__name__)


def upload_photo_to_cloudinary(file: UploadFile):
    """Upload photo to Cloudinary and return the URL"""
    try:
        upload_result = cloudinary.uploader.upload(file.file)
        return upload_result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Cloudinary upload failed: {str(e)}"
        )


def get_patient(db: Session, patient_id: int, mask: bool = True):
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
    if db_patient and mask:
        db_patient.nric = db_patient.mask_nric
    return db_patient


def get_patients(
    db: Session,
    mask: bool = True,
    pageNo: int = 0,
    pageSize: int = 10,
    name: Optional[str] = None,
    isActive: Optional[str] = None,
):
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

    db_patients = (
        query.order_by(Patient.name.asc()).offset(offset).limit(pageSize).all()
    )

    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    return db_patients, totalRecords, totalPages


def _patient_to_dict(patient) -> Dict[str, Any]:
    """Convert patient model to dictionary for messaging"""
    try:
        if hasattr(patient, "__dict__"):
            patient_dict = {}
            for key, value in patient.__dict__.items():
                if not key.startswith("_"):
                    # Convert datetime objects to ISO format strings
                    if hasattr(value, "isoformat"):
                        patient_dict[key] = value.isoformat()
                    else:
                        patient_dict[key] = value
            return patient_dict
        else:
            return {}
    except Exception as e:
        logger.error(f"Error converting patient to dict: {str(e)}")
        return {}


def create_patient(db: Session, patient: PatientCreate, user: str, user_full_name: str):
    """Create a new patient with message queue publishing"""

    # Check NRIC uniqueness
    existing_patient = (
        db.query(Patient)
        .filter(Patient.nric == patient.nric, Patient.isDeleted == "0")
        .first()
    )
    if existing_patient:
        raise HTTPException(
            status_code=400, detail="NRIC must be unique for active records"
        )

    query = text(
        """
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
    """
    )

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
        "createdDate": datetime.utcnow(),
        "modifiedDate": datetime.utcnow(),
        "CreatedById": user,
        "ModifiedById": user,
        "isDeleted": patient.isDeleted,
    }

    db.execute(query, params)
    db.commit()

    # Retrieve the newly inserted patient using NRIC
    new_patient = db.query(Patient).filter(Patient.nric == patient.nric).first()

    try:
        patient_data_dict = {
            k: serialize_data(v)
            for k, v in new_patient.__dict__.items()
            if not k.startswith("_")
        }
    except Exception:
        patient_data_dict = "{}"

    # Log the action
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

    # Publish patient creation event to message queue
    try:
        publisher = get_patient_publisher()
        patient_dict = _patient_to_dict(new_patient)
        success = publisher.publish_patient_created(
            patient_id=new_patient.id, patient_data=patient_dict, created_by=user
        )
        if not success:
            logger.warning(
                f"Failed to publish PATIENT_CREATED event for patient {new_patient.id}"
            )
    except Exception as e:
        logger.error(f"Error publishing patient creation event: {str(e)}")
        # Don't fail the operation if messaging fails

    return new_patient


def update_patient(
    db: Session, patient_id: int, patient: PatientUpdate, user: str, user_full_name: str
):
    """Update patient with message queue publishing"""
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Capture original data for change tracking
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
        original_patient_dict = _patient_to_dict(db_patient)
    except Exception:
        original_data_dict = "{}"
        original_patient_dict = {}

    # Check NRIC uniqueness
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
        raise HTTPException(
            status_code=400, detail="NRIC must be unique for active records"
        )

    # Track changes for messaging
    changes = {}
    patient_update_dict = patient.model_dump()

    for key, new_value in patient_update_dict.items():
        if hasattr(db_patient, key):
            old_value = getattr(db_patient, key)
            # Convert values to comparable formats
            if old_value != new_value:
                changes[key] = {
                    "old": serialize_data(old_value),
                    "new": serialize_data(new_value),
                }

    # Apply updates
    for key, value in patient_update_dict.items():
        setattr(db_patient, key, value)
    db_patient.modifiedDate = datetime.utcnow()
    db_patient.ModifiedById = user

    db.commit()
    db.refresh(db_patient)

    # Log the action
    updated_data_dict = serialize_data(patient.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=user,
        user_full_name=user_full_name,
        message="Updated Patient",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    # Publish patient update event to message queue
    try:
        publisher = get_patient_publisher()
        new_patient_dict = _patient_to_dict(db_patient)

        # Only publish if there were actual changes
        if changes:
            success = publisher.publish_patient_updated(
                patient_id=db_patient.id,
                old_data=original_patient_dict,
                new_data=new_patient_dict,
                changes=changes,
                modified_by=user,
            )
            if not success:
                logger.warning(
                    f"Failed to publish PATIENT_UPDATED event for patient {db_patient.id}"
                )
    except Exception as e:
        logger.error(f"Error publishing patient update event: {str(e)}")
        # Don't fail the operation if messaging fails

    return db_patient


def update_patient_profile_picture(
    db: Session, patient_id: int, file: UploadFile, user_id: str, user_full_name: str
):
    """Update only the patient's profile picture"""
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
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
    db_patient.modifiedDate = datetime.utcnow()
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


def delete_patient(db: Session, patient_id: int, user_id: str, user_full_name: str):
    """Soft delete patient with message queue publishing"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Capture original data before deletion
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
        patient_dict = _patient_to_dict(db_patient)
    except Exception:
        original_data_dict = "{}"
        patient_dict = {}

    # Perform soft delete
    setattr(db_patient, "isDeleted", "1")
    db_patient.modifiedDate = datetime.utcnow()
    db_patient.ModifiedById = user_id
    db.commit()
    db.refresh(db_patient)

    # Log the action
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

    # Publish patient deletion event to message queue
    try:
        publisher = get_patient_publisher()
        success = publisher.publish_patient_deleted(
            patient_id=db_patient.id, patient_data=patient_dict, deleted_by=user_id
        )
        if not success:
            logger.warning(
                f"Failed to publish PATIENT_DELETED event for patient {db_patient.id}"
            )
    except Exception as e:
        logger.error(f"Error publishing patient deletion event: {str(e)}")
        # Don't fail the operation if messaging fails

    return db_patient


def delete_patient_profile_picture(
    db: Session, patient_id: int, user_id: str, user_full_name: str
):
    """Remove the patient's profile picture by setting it to an empty string"""
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "0")
        .first()
    )
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
    db_patient.modifiedDate = datetime.utcnow()
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

#Hard delete patient from database, used for testing purposes only
def hard_delete_patient_records_by_id(
    db: Session, patient_id: int, user_id: str, user_full_name: str
):
    """Hard delete patient from database"""
    db_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "1")
        .first()
    )
    if not db_patient:
        raise HTTPException(status_code=404, detail="Soft Deleted Patient not found")

    # Capture original data before deletion
    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_patient.__dict__.items()
            if not k.startswith("_")
        }
        patient_dict = _patient_to_dict(db_patient)
    except Exception:
        original_data_dict = "{}"
        patient_dict = {}

    # Perform hard delete
    result = (
        db.query(Patient)
        .filter(Patient.id == patient_id, Patient.isDeleted == "1")
        .delete()
    )
    db.commit()
    print(f"Rows deleted: {result}")

    # Log the action
    log_crud_action(
        action=ActionType.DELETE,
        user=user_id,
        user_full_name=user_full_name,
        message="Hard Delete Patient",
        table="Patient",
        entity_id=patient_id,
        original_data=original_data_dict,
        updated_data=None,
    )

    # Publish patient deletion event to message queue
    try:
        publisher = get_patient_publisher()
        # need to use my own deleted function here? - bryan
        success = publisher.publish_patient_deleted(
            patient_id=patient_id, patient_data=patient_dict, deleted_by=user_id
        )
        if not success:
            logger.warning(
                f"Failed to publish HARD_DELETED_PATIENT event for patient {patient_id}"
            )
    except Exception as e:
        logger.error(f"Error publishing hard deletion patient event: {str(e)}")
        # Don't fail the operation if messaging fails

    return patient_dict
