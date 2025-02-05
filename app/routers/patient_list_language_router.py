from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.patient_list_language import PatientListLanguage, PatientListLanguageCreate, PatientListLanguageUpdate
from ..crud import patient_list_language_crud
router = APIRouter()

@router.get("/PatientListLanguage/{patient_list_language_id}", response_model=PatientListLanguage, description="Get Language by ID")
def get_patient_list_language(patient_list_language_id: int, db: Session = Depends(get_db)):
    return patient_list_language_crud.get_patient_list_language(db, patient_list_language_id)
   

@router.get("/PatientListLanguage/", response_model=list[PatientListLanguage], description="Get all Languages")
def get_all_patient_list_language(db: Session = Depends(get_db)):
    return patient_list_language_crud.get_all_patient_list_language(db)

@router.post("/PatientListLanguage/add", response_model=PatientListLanguage, description="Create Language")
def create_patient_list_language(patient_list_language: PatientListLanguageCreate, db: Session = Depends(get_db)):
    return patient_list_language_crud.create_patient_list_language(db, patient_list_language)

@router.put("/PatientListLanguage/update", response_model=PatientListLanguage, description="Update Language")
def update_patient_list_language(patient_list_language_id: int, patient_list_language: PatientListLanguageUpdate, db: Session = Depends(get_db)):
    return patient_list_language_crud.update_patient_list_language(db, patient_language_id=patient_list_language_id, patient_language= patient_list_language)

@router.delete("/PatientListLanguage/delete", response_model=PatientListLanguage, description="Delete Language")
def delete_patient_list_language(patient_list_language_id: int, db: Session = Depends(get_db)):
    db_patient_list_language = patient_list_language_crud.delete_patient_list_language(db, patient_language_id=patient_list_language_id)
    if not db_patient_list_language:
        raise HTTPException(status_code=404, detail="Language entry not found")
    return db_patient_list_language
    
