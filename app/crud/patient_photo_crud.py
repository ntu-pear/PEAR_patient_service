from sqlalchemy.orm import Session
from ..models.patient_photo_model import PatientPhoto
from ..schemas.patient_photo import PatientPhotoCreate, PatientPhotoUpdate

def get_patient_photos(db: Session, patient_id: int):
    return db.query(PatientPhoto).filter(PatientPhoto.patient_id == patient_id).all()

def get_album_by_category(db: Session, album_category_list_id: int):
    return db.query(PatientPhoto).filter(PatientPhoto.album_category_list_id == album_category_list_id).all()

def get_max_patient_photo(db: Session):
    return db.query(PatientPhoto).order_by(PatientPhoto.id.desc()).first()

def create_patient_photo(db: Session, photo: PatientPhotoCreate):
    db_photo = PatientPhoto(**photo.model_dump())
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

def update_patient_photo(db: Session, photo_id: int, photo: PatientPhotoUpdate):
    db_photo = db.query(PatientPhoto).filter(PatientPhoto.id == photo_id).first()
    if db_photo:
        for key, value in photo.model_dump().items():
            setattr(db_photo, key, value)
        db.commit()
        db.refresh(db_photo)
    return db_photo

def delete_patient_photo(db: Session, photo_id: int, photo: PatientPhotoUpdate):
    db_photo = db.query(PatientPhoto).filter(PatientPhoto.id == photo_id).first()
    if db_photo:
        for key, value in photo.model_dump().items():
            setattr(db_photo, key, value)
        db.commit()
        db.refresh(db_photo)
    return db_photo
