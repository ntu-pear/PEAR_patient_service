from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_photo_list_album_crud as crud_photo_list_album
from ..database import get_db
from ..schemas.patient_photo_list_album import (
    PatientPhotoListAlbum,
    PatientPhotoListAlbumCreate,
    PatientPhotoListAlbumUpdate,
)

router = APIRouter()


@router.get("/get_photo_list_albums", response_model=list[PatientPhotoListAlbum], description="Get all photo list albums.")
def get_photo_list_albums(request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    _ = extract_jwt_payload(request, require_auth)
    return crud_photo_list_album.get_all_photo_list_albums(db)


@router.get("/get_photo_list_album/{album_id}", response_model=PatientPhotoListAlbum, description="Get photo list album by ID.")
def get_photo_list_album(album_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    _ = extract_jwt_payload(request, require_auth)
    db_album = crud_photo_list_album.get_photo_list_album_by_id(db, album_id)
    if not db_album:
        raise HTTPException(status_code=404, detail="Photo list album not found")
    return db_album


@router.post("/create_photo_list_album", response_model=PatientPhotoListAlbum, description="Create a new photo list album.")
def create_photo_list_album(album: PatientPhotoListAlbumCreate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return crud_photo_list_album.create_photo_list_album(db, album, user_id, user_full_name)


@router.put("/update_photo_list_album/{album_id}", response_model=PatientPhotoListAlbum, description="Update a photo list album by ID.")
def update_photo_list_album(album_id: int, album: PatientPhotoListAlbumUpdate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_album = crud_photo_list_album.update_photo_list_album(db, album_id, album, user_id, user_full_name)
    return db_album


@router.delete("/delete_photo_list_album/{album_id}", response_model=PatientPhotoListAlbum, description="Soft delete a photo list album by marking it as deleted.")
def delete_photo_list_album(album_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_album = crud_photo_list_album.delete_photo_list_album(db, album_id, user_id, user_full_name)
    return db_album