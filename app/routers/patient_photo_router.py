from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud.patient_photo_crud import (
    create_patient_photo,
    delete_patient_photo,
    delete_patient_photo_by_photo_id,
    get_patient_photo_by_id,
    get_patient_photo_by_photo_id,
    get_patient_photos,
    update_patient_photo,
    update_patient_photo_by_photo_id,
)
from ..database import get_db
from ..schemas.patient_photo import *

router = APIRouter()


@router.post("/PersonalPhoto/upload", response_model=PatientPhotoResponse)
async def upload_patient_photo(
    request: Request,
    file: UploadFile = File(...),
    photo_data: PatientPhotoCreate = Depends(),
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Upload a new patient photo """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return create_patient_photo(db, file.file, photo_data, user_id, user_full_name)


@router.get("/PersonalPhotos", response_model=list[PatientPhotoResponse])
async def get_photos(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Retrieve all active patient photos """
    _ = extract_jwt_payload(request, require_auth)
    photos = get_patient_photos(db)
    return photos


@router.get("/PersonalPhotos/by-patient-id/{patient_id}", response_model=PatientPhotoResponse)
async def get_photo_by_patient_id(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Retrieve a specific patient photo by PatientID """
    _ = extract_jwt_payload(request, require_auth)
    photo = get_patient_photo_by_id(db, patient_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or deleted")
    return photo


@router.get("/PersonalPhotos/by-photo-id/{photo_id}", response_model=PatientPhotoResponse)
async def get_photo_by_photo_id(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Retrieve a specific patient photo by PatientPhotoID """
    _ = extract_jwt_payload(request, require_auth)
    photo = get_patient_photo_by_photo_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or deleted")
    return photo


@router.put("/PersonalPhoto/by-patient-id/{patient_id}", response_model=PatientPhotoResponse)
async def update_photo_by_patient_id(
    request: Request,
    patient_id: int,
    file: UploadFile = File(...),
    update_data: PatientPhotoUpdate = Depends(),
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Update a patient's photo by PatientID (replace `PhotoPath` with latest) """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    photo = update_patient_photo(db, patient_id, file.file, update_data, user_id, user_full_name)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.put("/PersonalPhoto/by-photo-id/{photo_id}", response_model=PatientPhotoResponse)
async def update_photo_by_photo_id(
    request: Request,
    photo_id: int,
    file: UploadFile = File(...),  # Compulsory file upload
    update_data: PatientPhotoUpdate = Depends(),
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ 
    Update a patient's photo by PatientPhotoID
    - Requires file upload to replace the PhotoPath
    - Can also update PhotoDetails and AlbumCategoryListID
    """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    photo = update_patient_photo_by_photo_id(db, photo_id, file.file, update_data, user_id, user_full_name)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.delete("/PersonalPhoto/by-patient-id/{patient_id}")
async def delete_photo_by_patient_id(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ Soft delete all photos for a specific patient by PatientID """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    photo = delete_patient_photo(db, patient_id, user_id, user_full_name)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo(s) deleted successfully"}


@router.delete("/PersonalPhoto/by-photo-id/{photo_id}")
async def delete_photo_by_photo_id(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """ 
    Soft delete a specific photo by PatientPhotoID 
    Also deletes the photo from Cloudinary
    """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    photo = delete_patient_photo_by_photo_id(db, photo_id, user_id, user_full_name)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo deleted successfully", "photo_id": photo_id}