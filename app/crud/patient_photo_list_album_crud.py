from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.patient_photo_list_album_model import PatientPhotoListAlbum
from ..schemas.patient_photo_list_album import PatientPhotoListAlbumCreate, PatientPhotoListAlbumUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data


def get_all_photo_list_albums(db: Session):
    """Get all active photo list albums"""
    return db.query(PatientPhotoListAlbum).filter(PatientPhotoListAlbum.IsDeleted == 0).all()


def get_photo_list_album_by_id(db: Session, album_id: int):
    """Get photo list album by ID (only if not deleted)"""
    return (
        db.query(PatientPhotoListAlbum)
        .filter(PatientPhotoListAlbum.AlbumCategoryListID == album_id, PatientPhotoListAlbum.IsDeleted == 0)
        .first()
    )


def create_photo_list_album(db: Session, album: PatientPhotoListAlbumCreate, created_by: str, user_full_name: str):
    """Create a new photo list album"""
    
    # Check if Value already exists in the DB (duplicate validation)
    existing = db.query(PatientPhotoListAlbum).filter(
        PatientPhotoListAlbum.Value == album.Value,
        PatientPhotoListAlbum.IsDeleted == 0
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Photo list album with name '{album.Value}' already exists"
        )
    
    db_album = PatientPhotoListAlbum(
        Value=album.Value,
        IsDeleted=album.IsDeleted,
        CreatedDateTime=datetime.now(),
        UpdatedDateTime=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by
    )
    
    updated_data_dict = serialize_data(album.model_dump())
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created photo list album",
        table="PatientPhotoListAlbum",
        entity_id=db_album.AlbumCategoryListID,
        original_data=None,
        updated_data=updated_data_dict,
    )
    
    return db_album


def update_photo_list_album(
    db: Session, album_id: int, album: PatientPhotoListAlbumUpdate, modified_by: str, user_full_name: str
):
    """Update photo list album by ID"""
    db_album = (
        db.query(PatientPhotoListAlbum)
        .filter(PatientPhotoListAlbum.AlbumCategoryListID == album_id)
        .first()
    )

    if not db_album:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    
    if db_album.IsDeleted == 1:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    
    # Check for duplicate Value if it's being updated
    if album.Value is not None and album.Value != db_album.Value:
        existing = db.query(PatientPhotoListAlbum).filter(
            PatientPhotoListAlbum.Value == album.Value,
            PatientPhotoListAlbum.IsDeleted == 0,
            PatientPhotoListAlbum.AlbumCategoryListID != album_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Photo list album with name '{album.Value}' already exists"
            )
    
    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_album.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"
    
    for key, value in album.model_dump(exclude_unset=True).items():
        setattr(db_album, key, value)

    # Set UpdatedDateTime to the current datetime
    db_album.UpdatedDateTime = datetime.now()

    # Update the modifiedById field
    db_album.ModifiedById = modified_by

    db.commit()
    db.refresh(db_album)
    
    updated_data_dict = serialize_data(album.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Updated photo list album",
        table="PatientPhotoListAlbum",
        entity_id=album_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
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
    
    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Deleted photo list album",
        table="PatientPhotoListAlbum",
        entity_id=album_id,
        original_data=original_data_dict,
        updated_data=None,
    )
    
    return db_album