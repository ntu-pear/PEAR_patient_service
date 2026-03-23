from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_photo_list_album_model import PatientPhotoListAlbum
from ..schemas.patient_photo_list_album import (
    PatientPhotoListAlbumCreate,
    PatientPhotoListAlbumUpdate,
)


def get_all_photo_list_albums(db: Session):
    """Get all active photo list albums"""
    return db.query(PatientPhotoListAlbum).filter(PatientPhotoListAlbum.IsDeleted == 0).order_by(PatientPhotoListAlbum.Value.asc()).all()


def get_photo_list_album_by_id(db: Session, album_id: int):
    """Get photo list album by ID (only if not deleted)"""
    return (
        db.query(PatientPhotoListAlbum)
        .filter(PatientPhotoListAlbum.AlbumCategoryListID == album_id, PatientPhotoListAlbum.IsDeleted == 0)
        .first()
    )


def create_photo_list_album(db: Session, album: PatientPhotoListAlbumCreate, created_by: str, user_full_name: str):
    """Create a new photo list album with duplicate check and uppercase transformation"""
    
    # Convert Value to UPPERCASE before checking and inserting
    uppercase_value = album.Value.upper()
    
    # Check if Value already exists in the DB (duplicate validation)
    existing = db.query(PatientPhotoListAlbum).filter(
        PatientPhotoListAlbum.Value == uppercase_value,
        PatientPhotoListAlbum.IsDeleted == 0
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Photo list album with name '{uppercase_value}' already exists"
        )
    
    db_album = PatientPhotoListAlbum(
        Value=uppercase_value,
        IsDeleted=album.IsDeleted,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by
    )
    
    updated_data_dict = serialize_data({"Value": uppercase_value, "IsDeleted": album.IsDeleted})
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message=f"Created photo album category: {db_album.Value}",
        table="PatientPhotoListAlbum",
        entity_id=db_album.AlbumCategoryListID,
        original_data=None,
        updated_data=updated_data_dict,
        log_type = 'system',
        is_system_config = True,
    )
    
    return db_album


def update_photo_list_album(
    db: Session, album_id: int, album: PatientPhotoListAlbumUpdate, modified_by: str, user_full_name: str
):
    """Update photo list album by ID with uppercase transformation"""
    db_album = (
        db.query(PatientPhotoListAlbum)
        .filter(PatientPhotoListAlbum.AlbumCategoryListID == album_id)
        .first()
    )

    if not db_album:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    
    if db_album.IsDeleted == 1:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    
    # Convert Value to UPPERCASE if it's being updated
    update_data = album.model_dump(exclude_unset=True)
    if "Value" in update_data and update_data["Value"] is not None:
        uppercase_value = update_data["Value"].upper()
        
        # Check for duplicate Value if it's being updated
        if uppercase_value != db_album.Value:
            existing = db.query(PatientPhotoListAlbum).filter(
                PatientPhotoListAlbum.Value == uppercase_value,
                PatientPhotoListAlbum.IsDeleted == 0,
                PatientPhotoListAlbum.AlbumCategoryListID != album_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Photo list album with name '{uppercase_value}' already exists"
                )
        
        update_data["Value"] = uppercase_value
    
    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_album.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"
    
    for key, value in update_data.items():
        setattr(db_album, key, value)

    # Set UpdatedDateTime to the current datetime
    db_album.UpdatedDateTime = datetime.now()

    # Update the modifiedById field
    db_album.ModifiedById = modified_by

    db.commit()
    db.refresh(db_album)
    
    updated_data_dict = serialize_data(update_data)
    updated_data_dict["Value"] = db_album.Value
    original_data_dict["Value"] = db_album.Value

    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        user_full_name=user_full_name,
        message=f"Updated photo list category: {db_album.Value}",
        table="PatientPhotoListAlbum",
        entity_id=album_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
        log_type = 'system',
        is_system_config = True,
    )
    
    return db_album



def delete_photo_list_album(db: Session, album_id: int, modified_by: str, user_full_name: str):
    """Soft delete photo list album by marking it as deleted"""
    db_album = (
        db.query(PatientPhotoListAlbum)
        .filter(PatientPhotoListAlbum.AlbumCategoryListID == album_id)
        .first()
    )

    if not db_album or db_album.IsDeleted == 1:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    
    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_album.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"
    
    # Soft delete by marking the record as deleted
    db_album.IsDeleted = 1
    db_album.UpdatedDateTime = datetime.now()
    db_album.ModifiedById = modified_by
    db.commit()

    original_data_dict['Value'] = db_album.Value
    
    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message=f"Deleted photo album category: {db_album.Value}",
        table="PatientPhotoListAlbum",
        entity_id=album_id,
        original_data=original_data_dict,
        updated_data=None,
        log_type = 'system',
        is_system_config = True,
    )
    
    return db_album