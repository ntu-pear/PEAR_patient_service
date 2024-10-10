from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_allergy_mapping_crud
from ..schemas.patient_allergy_mapping import PatientAllergy, PatientAllergyCreate

router = APIRouter()

@router.get("/get_all_patient_allergies", response_model=list[PatientAllergy], description="Get all patient allergies.")
def get_all_patient_allergies(db: Session = Depends(get_db)):
    result = patient_allergy_mapping_crud.get_all_allergies(db)
    if not result:
        raise HTTPException(status_code=404, detail="No allergies found")
    return result


@router.get("/get_patient_allergy/{patient_id}", response_model=list[PatientAllergy], description="Get patient allergies by patient ID.")
def get_patient_allergy(patient_id: int, db: Session = Depends(get_db)):
    result = patient_allergy_mapping_crud.get_patient_allergies(db, patient_id)
    if not result:
        raise HTTPException(status_code=404, detail="No allergies found for this patient")
    return result

@router.post("/create_patient_allergy", response_model=PatientAllergy, description="Create a new patient allergy record.")
def create_patient_allergy(allergy_data: PatientAllergyCreate, db: Session = Depends(get_db)):
    return patient_allergy_mapping_crud.create_patient_allergy(db, allergy_data)
