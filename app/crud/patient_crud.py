from sqlalchemy.orm import Session
from sqlalchemy import func, text
import cloudinary.uploader
from ..models.patient_model import Patient
from ..schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
import math
from fastapi import HTTPException, UploadFile


# To Change
user = "1"
SYSTEM_USER_ID  = "1"


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


def get_patients(db: Session, mask: bool = True, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    db_patients = (
        db.query(Patient)
        .filter(Patient.isDeleted == "0")
        .order_by(Patient.id)
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    totalRecords = (
        db.query(func.count())
        .select_from(Patient)
        .filter(Patient.isDeleted == "0")
        .scalar()
    )
    totalPages = math.ceil(totalRecords / pageSize)
    if db_patients and mask:
        for db_patient in db_patients:
            db_patient.nric = db_patient.mask_nric
    return db_patients, totalRecords, totalPages


def create_patient(db: Session, patient: PatientCreate, user: str, user_full_name: str):
    """ Create a new patient while explicitly avoiding OUTPUT inserted.id """

    # Check NRIC uniqueness
    existing_patient = (
        db.query(Patient)
        .filter(Patient.nric == patient.nric, Patient.isDeleted == "0")
        .first()
    )
    if existing_patient:
        raise HTTPException(status_code=400, detail="NRIC must be unique for active records")

    query = text("""
        INSERT INTO [PATIENT] (
            active, name, nric, address, [tempAddress], [homeNo], [handphoneNo], gender, 
            [dateOfBirth], [isApproved], [preferredName], [preferredLanguageId], [updateBit], 
            [autoGame], [startDate], [endDate], [isActive], [isRespiteCare], [privacyLevel], 
            [terminationReason], [inActiveReason], [inActiveDate], [profilePicture], [createdDate], 
            [modifiedDate], [CreatedById], [ModifiedById], [isDeleted]
        ) VALUES (
            :active, :name, :nric, :address, :tempAddress, :homeNo, :handphoneNo, :gender, 
            :dateOfBirth, :isApproved, :preferredName, :preferredLanguageId, :updateBit, 
            :autoGame, :startDate, :endDate, :isActive, :isRespiteCare, :privacyLevel, 
            :terminationReason, :inActiveReason, :inActiveDate, :profilePicture, :createdDate, 
            :modifiedDate, :CreatedById, :ModifiedById, :isDeleted
        );
    """)

    params = {
        "active": patient.active,
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
    return new_patient


def update_patient(db: Session, patient_id: int, patient: PatientUpdate, user: str, user_full_name: str):
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
        raise HTTPException(status_code=400, detail="NRIC must be unique for active records")

    for key, value in patient.model_dump().items():
        setattr(db_patient, key, value)
    db_patient.modifiedDate = datetime.utcnow()
    db_patient.ModifiedById = user

    db.commit()
    db.refresh(db_patient)

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

    return db_patient


def update_patient_profile_picture(db: Session, patient_id: int, file: UploadFile, user: str, user_full_name: str):
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

    # # Log original data
    # original_data_dict = {"profilePicture": db_patient.profilePicture}

    # Update patient profile picture
    db_patient.profilePicture = profile_picture_url
    db_patient.modifiedDate = datetime.utcnow()
    db_patient.ModifiedById = SYSTEM_USER_ID
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
        user=user,
        user_full_name=user_full_name,
        message="Updated Patient Photo",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    return db_patient


def delete_patient(db: Session, patient_id: int, user: str, user_full_name: str):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
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

    setattr(db_patient, "isDeleted", "1")
    db.commit()

    log_crud_action(
        action=ActionType.DELETE,
        user=user,
        user_full_name=user_full_name,
        message="Deleted Patient",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data= None,
    )

    return db_patient

def delete_patient_profile_picture(db: Session, patient_id: int, user: str, user_full_name: str):
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
    db_patient.modifiedDate = datetime.utcnow()
    db_patient.ModifiedById = SYSTEM_USER_ID
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
        user=user,
        user_full_name=user_full_name,
        message="Deleted Patient Photo",
        table="Patient",
        entity_id=db_patient.id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )

    return db_patient
