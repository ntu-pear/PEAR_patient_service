from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_photo_crud as crud_photo
from ..schemas import patient_photo as schemas_photo

router = APIRouter()

@router.get("/PatientPhoto", response_model=list[schemas_photo.PatientPhoto])
def get_patient_photos(patient_id: int, db: Session = Depends(get_db)):
    return crud_photo.get_patient_photos(db, patient_id)

@router.get("/PatientPhoto/GetAlbumByCategory", response_model=list[schemas_photo.PatientPhoto])
def get_album_by_category(album_category_list_id: int, db: Session = Depends(get_db)):
    return crud_photo.get_album_by_category(db, album_category_list_id)

@router.get("/PatientPhoto/MaxPatientPhoto", response_model=schemas_photo.PatientPhoto)
def get_max_patient_photo(db: Session = Depends(get_db)):
    return crud_photo.get_max_patient_photo(db)

@router.post("/PatientPhoto/add", response_model=schemas_photo.PatientPhoto)
def create_patient_photo(photo: schemas_photo.PatientPhotoCreate, db: Session = Depends(get_db)):
    return crud_photo.create_patient_photo(db, photo)

@router.put("/PatientPhoto/update", response_model=schemas_photo.PatientPhoto)
def update_patient_photo(photo_id: int, photo: schemas_photo.PatientPhotoUpdate, db: Session = Depends(get_db)):
    db_photo = crud_photo.update_patient_photo(db, photo_id, photo)
    if not db_photo:
        raise HTTPException(status_code=404, detail="Patient photo not found")
    return db_photo

@router.put("/PatientPhoto/delete", response_model=schemas_photo.PatientPhoto)
def delete_patient_photo(photo_id: int, photo: schemas_photo.PatientPhotoUpdate, db: Session = Depends(get_db)):
    db_photo = crud_photo.delete_patient_photo(db, photo_id, photo)
    if not db_photo:
        raise HTTPException(status_code=404, detail="Patient photo not found")
    return db_photo
