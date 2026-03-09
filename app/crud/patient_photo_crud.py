import logging
import re
from datetime import datetime

import cloudinary.uploader
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_photo_model import PatientPhoto
from ..models.patient_model import Patient
from ..schemas.patient_photo import PatientPhotoCreate, PatientPhotoUpdate

logger = logging.getLogger(__name__)

def extract_public_id_from_url(cloudinary_url: str) -> str:
    """
    Extract the public_id from a Cloudinary URL.
    """
    try:
        # Remove version number and extension from cloudinary photo link
        match = re.search(r'/upload/(?:v\d+/)?(.+)\.\w+$', cloudinary_url)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        logger.error(f"Error extracting public_id from URL {cloudinary_url}: {str(e)}")
        return None

def delete_photo_from_cloudinary(cloudinary_url: str):
    """
    Delete photo from Cloudinary using the photo URL.
    Extracts the public_id from the URL and deletes it.
    """
    try:
        public_id = extract_public_id_from_url(cloudinary_url)
        if public_id:
            result = cloudinary.uploader.destroy(public_id)
            if result.get('result') == 'ok':
                logger.info(f"Successfully deleted photo from Cloudinary: {public_id}")
                return True
            else:
                logger.warning(f"Failed to delete photo from Cloudinary: {public_id}, Result: {result}")
                return False
        else:
            logger.error(f"Could not extract public_id from URL: {cloudinary_url}")
            return False
    except Exception as e:
        logger.error(f"Cloudinary deletion failed for URL {cloudinary_url}: {str(e)}")
        return False

def upload_photo_to_cloudinary(file):
    """ Upload photo to Cloudinary and return the URL """
    try:
        upload_result = cloudinary.uploader.upload(file)
        return upload_result["secure_url"]
    except Exception as e:
        raise ValueError(f"Cloudinary upload failed: {str(e)}")

def get_patient_photos(db: Session):
    """ Retrieve all active patient photos """
    return db.query(PatientPhoto).filter(
        PatientPhoto.IsDeleted == 0
    ).all()

def get_patient_photo_by_patient_id(db: Session, patient_id: int):
    """ Retrieve patient photos by based on patient ID (only if not deleted) """
    return db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patient_id,
        PatientPhoto.IsDeleted == 0
    ).all()
    
def get_patient_photo_by_photo_id(db: Session, patient_photo_id: int):
    """ Retrieve a single patient photo by PatientPhotoID (only if not deleted) """
    return db.query(PatientPhoto).filter(
        PatientPhoto.PatientPhotoID == patient_photo_id,
        PatientPhoto.IsDeleted == 0
    ).first()

def create_patient_photo(db: Session, file, photo_data: PatientPhotoCreate, created_by: str, user_full_name: str):
    """ Create a new patient photo record """
    
    # Upload photo to Cloudinary
    photo_url = upload_photo_to_cloudinary(file)

    # Create the PatientPhoto object
    db_photo = PatientPhoto(
        PhotoPath=photo_url,
        PhotoDetails=photo_data.PhotoDetails,
        AlbumCategoryListID=photo_data.AlbumCategoryListID,
        PatientID=photo_data.PatientID,
        IsDeleted=0,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by
    )

    # Save to DB
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == photo_data.PatientID).first()
        patient_name = patient.name if patient else None
    except Exception:
        patient_name = None

    updated_data_dict = serialize_data(photo_data.model_dump())
    updated_data_dict['PatientName'] = patient_name

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        table="PatientPhoto",
        entity_id=db_photo.PatientPhotoID,
        original_data=None,
        updated_data=updated_data_dict,
        user_full_name=user_full_name,
        message=f"Added photo for patient: {patient_name or 'Unknown'}",
        patient_id= photo_data.PatientID,
        patient_full_name= patient_name,
        log_type = 'patient_info',
        is_system_config = False,
    )
    return db_photo


def update_patient_photo(db: Session, patient_id: int, file, update_data: PatientPhotoUpdate, modified_by: str, user_full_name: str):
    """ Update patient photo by PatientID and replace PhotoPath with the latest uploaded photo """
    
    # Check if patient has an existing photo
    db_photo = db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patient_id,
        PatientPhoto.IsDeleted == 0
    ).first()

    if not db_photo:
        return None  # No photo found for this patient

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Delete old photo from Cloudinary
    old_photo_url = db_photo.PhotoPath
    delete_photo_from_cloudinary(old_photo_url)

    # Upload new photo to Cloudinary
    new_photo_url = upload_photo_to_cloudinary(file)
    db_photo.PhotoPath = new_photo_url

    # Update other fields if provided
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_photo, key, value)

    db_photo.UpdatedDateTime = datetime.now()
    db_photo.ModifiedById = modified_by

    db.commit()
    db.refresh(db_photo)

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        patient_name = patient.name if patient else None
    except Exception:
        patient_name = None

    updated_data_dict = serialize_data(update_data.model_dump())
    updated_data_dict['PatientName'] = patient_name
    original_data_dict['PatientName'] = patient_name

    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        table="PatientPhoto",
        entity_id=db_photo.PatientPhotoID,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        user_full_name=user_full_name,
        message=f"Updated photo for patient: {patient_name or 'Unknown'}",
        patient_id= patient_id,
        patient_full_name= patient_name,
        log_type = 'patient_info',
        is_system_config = False,
    )
    return db_photo


def update_patient_photo_by_photo_id(db: Session, patient_photo_id: int, file, update_data: PatientPhotoUpdate, modified_by: str, user_full_name: str):
    """ Update patient photo by PatientPhotoID and optionally replace PhotoPath with the latest uploaded photo """
    
    # Find the photo by PatientPhotoID
    db_photo = db.query(PatientPhoto).filter(
        PatientPhoto.PatientPhotoID == patient_photo_id,
        PatientPhoto.IsDeleted == 0
    ).first()

    if not db_photo:
        return None  # No photo found with this ID

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # If a new file is provided, delete old photo from Cloudinary and upload new one
    if file:
        # Delete old photo from Cloudinary
        old_photo_url = db_photo.PhotoPath
        delete_photo_from_cloudinary(old_photo_url)
        
        # Upload new photo to Cloudinary
        new_photo_url = upload_photo_to_cloudinary(file)
        db_photo.PhotoPath = new_photo_url

    # Update other fields if provided
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_photo, key, value)

    db_photo.UpdatedDateTime = datetime.now()
    db_photo.ModifiedById = modified_by

    db.commit()
    db.refresh(db_photo)

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == db_photo.PatientID).first()
        patient_name = patient.name if patient else None
    except Exception:
        patient_name = None

    updated_data_dict = serialize_data(update_data.model_dump())
    updated_data_dict['PatientName'] = patient_name
    original_data_dict['PatientName'] = patient_name

    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        table="PatientPhoto",
        entity_id=db_photo.PatientPhotoID,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        user_full_name=user_full_name,
        message=f"Update photo for patient: {patient_name or 'Unknown'}",
        patient_id = db_photo.PatientID,
        patient_full_name= patient_name,
        log_type = 'patient_info',
        is_system_config = False,
    )
    return db_photo


def delete_patient_photo(db: Session, patient_id: int, modified_by: str, user_full_name: str):
    """ Soft delete all photos for a given PatientID (set IsDeleted = 1) and delete from Cloudinary """
    
    # Get all photos for the patient
    db_photos = db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patient_id,
        PatientPhoto.IsDeleted == 0
    ).all()

    if not db_photos:
        return None  # No photos found for this patient

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        patient_name = patient.name if patient else None
    except Exception:
        patient_name = None

    cloudinary_deletion_results = []
    
    # Delete each photo from Cloudinary and soft delete in database
    for db_photo in db_photos:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        
        # Delete photo from Cloudinary
        cloudinary_deleted = delete_photo_from_cloudinary(db_photo.PhotoPath)
        cloudinary_deletion_results.append({
            "PatientPhotoID": db_photo.PatientPhotoID,
            "PhotoPath": db_photo.PhotoPath,
            "CloudinaryDeleted": cloudinary_deleted
        })
        
        if not cloudinary_deleted:
            logger.warning(f"Failed to delete photo from Cloudinary for PatientPhotoID {db_photo.PatientPhotoID}")
        
        # Soft delete in database
        db_photo.IsDeleted = 1
        db_photo.ModifiedById = modified_by
        db_photo.UpdatedDateTime = datetime.now()

        original_data_dict['PatientName'] = patient_name
        
        # Log each photo deletion
        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            table="PatientPhoto",
            entity_id=db_photo.PatientPhotoID,
            original_data=original_data_dict,
            updated_data=None,
            user_full_name=user_full_name,
            message=f"Delete patient photo for {patient_name or 'Unknown'} (Cloudinary deletion: {cloudinary_deleted})",
            patient_id= patient_id,
            patient_full_name= patient_name,
            log_type = 'patient_info',
            is_system_config = False,
        )
    
    db.commit()

    # Log summary of all deletions
    logger.info(f"Deleted {len(db_photos)} photos for PatientID {patient_id}. Cloudinary results: {cloudinary_deletion_results}")
    
    return db_photos


def delete_patient_photo_by_photo_id(db: Session, patient_photo_id: int, modified_by: str, user_full_name: str):
    """ Soft delete a photo by PatientPhotoID (set IsDeleted = 1) and delete from Cloudinary """
    
    # Find the photo by PatientPhotoID
    db_photo = db.query(PatientPhoto).filter(
        PatientPhoto.PatientPhotoID == patient_photo_id,
        PatientPhoto.IsDeleted == 0
    ).first()

    if not db_photo:
        return None  # No photo found with this ID

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Delete photo from Cloudinary
    cloudinary_deleted = delete_photo_from_cloudinary(db_photo.PhotoPath)
    
    if not cloudinary_deleted:
        logger.warning(f"Failed to delete photo from Cloudinary for PatientPhotoID {patient_photo_id}")

    # Soft delete in database
    db_photo.IsDeleted = 1
    db_photo.ModifiedById = modified_by
    db_photo.UpdatedDateTime = datetime.now()
    
    db.commit()

    # Fetch patient name for logging
    try:
        patient = db.query(Patient).filter(Patient.id == db_photo.PatientID).first()
        patient_name = patient.name if patient else None
    except Exception:
        patient_name = None

    original_data_dict['PatientName'] = patient_name

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        table="PatientPhoto",
        entity_id=patient_photo_id,
        original_data=original_data_dict,
        updated_data=None,
        user_full_name=user_full_name,
        message=f"Deleted photo for patient: {patient_name or 'Unknown'} (Cloudinary deletion: {cloudinary_deleted})",
        patient_id = db_photo.PatientID,
        patient_full_name= patient_name,
        log_type = 'patient_info',
        is_system_config = False,
    )
    return db_photo