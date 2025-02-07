from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.patient_photo import *
from ..crud.patient_photo_crud import (
    create_patient_photo,
    get_patient_photos,
    get_patient_photo_by_id,
    update_patient_photo,
    delete_patient_photo
)

router = APIRouter()

PATIENT_ID = 2  # Fixed PatientID for all API calls

@router.post("/", response_model=PatientPhotoResponse)
async def upload_patient_photo(
    file: UploadFile = File(...),
    photo_data: PatientPhotoCreate = Depends(),
    db: Session = Depends(get_db)
):
    """ Upload a new patient photo (PatientID always = 2) """
    photo_data.PatientID = PATIENT_ID  # Override PatientID
    return create_patient_photo(db, file.file, photo_data)

@router.get("/", response_model=list[PatientPhotoResponse])
async def get_photos(db: Session = Depends(get_db)):
    """ Retrieve all active patient photos """
    photos = get_patient_photos(db)
    return photos

@router.get("/{photo_id}", response_model=PatientPhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """ Retrieve a specific patient photo """
    photo = get_patient_photo_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found or deleted")
    return photo

@router.put("/{patient_id}", response_model=PatientPhotoResponse)
async def update_photo(
    patient_id: int,
    file: UploadFile = File(...),
    update_data: PatientPhotoUpdate = Depends(),
    db: Session = Depends(get_db)
):
    """ Update a patient's photo (replace `PhotoPath` with latest) """
    photo = update_patient_photo(db, patient_id, file.file, update_data)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.delete("/{patient_id}")
async def delete_photo(patient_id: int, modified_by_id: int, db: Session = Depends(get_db)):
    """ Soft delete a specific patient photo """
    photo = delete_patient_photo(db, patient_id, modified_by_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"message": "Photo deleted successfully"}
