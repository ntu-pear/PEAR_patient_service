from sqlalchemy.orm import Session
import cloudinary.uploader
from ..models.patient_photo_model import PatientPhoto
from ..schemas.patient_photo import PatientPhotoCreate, PatientPhotoUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

PATIENT_ID = 2  # Fixed Patient ID
SYSTEM_USER_ID = "1"  # System-generated default user ID

def upload_photo_to_cloudinary(file):
    """ Upload photo to Cloudinary and return the URL """
    try:
        upload_result = cloudinary.uploader.upload(file)
        return upload_result["secure_url"]
    except Exception as e:
        raise ValueError(f"Cloudinary upload failed: {str(e)}")

def create_patient_photo(db: Session, file, photo_data: PatientPhotoCreate):
    """ Create a new patient photo record with system-generated defaults """
    
    # Upload photo to Cloudinary
    photo_url = upload_photo_to_cloudinary(file)

    # Create the PatientPhoto object with default system values
    db_photo = PatientPhoto(
        PhotoPath=photo_url,
        PhotoDetails=photo_data.PhotoDetails,
        AlbumCategoryListID=photo_data.AlbumCategoryListID,
        PatientID=PATIENT_ID,  # Default to 2
        IsDeleted=0,  # Default to active photo
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=SYSTEM_USER_ID,  # Default system user
        ModifiedById=SYSTEM_USER_ID  # Default system user
    )

    updated_data_dict = serialize_data(photo_data.model_dump())
    # Save to DB
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        table="PatientPhoto",
        entity_id=db_photo.PhotoID,
        original_data=None,
        updated_data=updated_data_dict,
        user_full_name="None",
        message="Create patient photo",
    )
    return db_photo

def get_patient_photos(db: Session):
    """ Retrieve all active patient photos """
    return db.query(PatientPhoto).filter(
        PatientPhoto.IsDeleted == 0
    ).all()

def get_patient_photo_by_id(db: Session, patienti_id: int):
    """ Retrieve a single patient photo by ID (only if not deleted) """
    return db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patienti_id,
        PatientPhoto.IsDeleted == 0
    ).first()


def update_patient_photo(db: Session, patient_id: int, file, update_data: PatientPhotoUpdate):
    """ Update patient photo by PatientID and replace PhotoPath with the latest uploaded photo """
    
    # Check if patient has an existing photo
    db_photo = db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patient_id,
        PatientPhoto.IsDeleted == 0
    ).first()

    if not db_photo:
        return None  # No photo found for this patient

    # Upload new photo to Cloudinary
    new_photo_url = upload_photo_to_cloudinary(file)

    # Update only provided fields
    db_photo.PhotoPath = new_photo_url  # Replace the path with the latest photo

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_photo, key, value)

    db_photo.UpdatedDateTime = datetime.now()

    db.commit()
    db.refresh(db_photo)

    updated_data_dict = serialize_data(update_data.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=SYSTEM_USER_ID,
        table="PatientPhoto",
        entity_id=db_photo.PhotoID,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        user_full_name="None",
        message="Update patient photo",
    )
    return db_photo

def delete_patient_photo(db: Session, patient_id: int, modified_by_id: int):
    """ Soft delete all photos for a given PatientID (set IsDeleted = 1) """
    
    # Get all photos for the patient
    db_photos = db.query(PatientPhoto).filter(
        PatientPhoto.PatientID == patient_id,
        PatientPhoto.IsDeleted == 0
    ).all()

    if not db_photos:
        return None  # No photos found for this patient

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_photo.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    for db_photo in db_photos:
        db_photo.IsDeleted = 1
        db_photo.ModifiedById = modified_by_id
        db_photo.UpdatedDateTime = datetime.now()
    
    db.commit()

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by_id,
        table="PatientPhoto",
        entity_id=patient_id,
        original_data=original_data_dict,
        updated_data=None,
        user_full_name="None",
        message="Delete patient photo",
    )
    return db_photos

