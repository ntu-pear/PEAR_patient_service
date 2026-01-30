from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

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

PATIENT_ID = 2  # Fixed PatientID for all API calls

@router.post("/PersonalPhoto/upload", response_model=PatientPhotoResponse)
async def upload_patient_photo(
    file: UploadFile = File(...),
    photo_data: PatientPhotoCreate = Depends(),
    db: Session = Depends(get_db)
):
    """ Upload a new patient photo (PatientID always = 2) """
    photo_data.PatientID = PATIENT_ID  # Override PatientID
    return create_patient_photo(db, file.file, photo_data)

@router.get("/PersonalPhotos", response_model=list[PatientPhotoResponse])
async def get_photos(db: Session = Depends(get_db)):
    """ Retrieve all active patient photos """
    photos = get_patient_photos(db)
    return photos

@router.get("/PersonalPhotos/by-patient-id/{patient_id}", response_model=PatientPhotoResponse)
async def get_photo_by_patient_id(patient_id: int, db: Session = Depends(get_db)):
    """ Retrieve a specific patient photo by PatientID """
    photo = get_patient_photo_by_id(db, patient_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or deleted")
    return photo

@router.get("/PersonalPhotos/by-photo-id/{photo_id}", response_model=PatientPhotoResponse)
async def get_photo_by_photo_id(photo_id: int, db: Session = Depends(get_db)):
    """ Retrieve a specific patient photo by PatientPhotoID """
    photo = get_patient_photo_by_photo_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or deleted")
    return photo

@router.put("/PersonalPhoto/update/by-patient-id/{patient_id}", response_model=PatientPhotoResponse)
async def update_photo_by_patient_id(
    patient_id: int,
    file: UploadFile = File(...),
    update_data: PatientPhotoUpdate = Depends(),
    db: Session = Depends(get_db)
):
    """ Update a patient's photo by PatientID (replace `PhotoPath` with latest) """
    photo = update_patient_photo(db, patient_id, file.file, update_data)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.put("/PersonalPhoto/update/by-photo-id/{photo_id}", response_model=PatientPhotoResponse)
async def update_photo_by_photo_id(
    photo_id: int,
    file: UploadFile = File(None),  # Optional file upload
    update_data: PatientPhotoUpdate = Depends(),
    db: Session = Depends(get_db)
):
    """ 
    Update a patient's photo by PatientPhotoID
    - If file is provided, replaces the PhotoPath with the new uploaded photo
    - Can update PhotoDetails and other metadata without uploading a new file
    """
    photo = update_patient_photo_by_photo_id(db, photo_id, file.file if file else None, update_data)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.delete("/PersonalPhoto/delete/by-patient-id/{patient_id}")
async def delete_photo_by_patient_id(patient_id: int, modified_by_id: str, db: Session = Depends(get_db)):
    """ Soft delete all photos for a specific patient by PatientID """
    photo = delete_patient_photo(db, patient_id, modified_by_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo(s) deleted successfully"}

@router.delete("/PersonalPhoto/delete/by-photo-id/{photo_id}")
async def delete_photo_by_photo_id(photo_id: int, modified_by_id: str, db: Session = Depends(get_db)):
    """ 
    Soft delete a specific photo by PatientPhotoID 
    Also deletes the photo from Cloudinary
    """
    photo = delete_patient_photo_by_photo_id(db, photo_id, modified_by_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo deleted successfully", "photo_id": photo_id}