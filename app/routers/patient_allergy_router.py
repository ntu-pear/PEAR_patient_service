from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_allergy_crud as crud_allergy
from ..schemas.patient_allergy import (
    PatientAllergy,
    PatientAllergyCreate,
    PatientAllergyUpdate
)

router = APIRouter()

@router.get("/Allergy", response_model=list[PatientAllergy])
def get_allergies(db: Session = Depends(get_db)):
    return crud_allergy.get_allergies(db)

@router.get("/Allergy/PatientAllergy", response_model=list[PatientAllergy])
def get_patient_allergy(patient_id: int, db: Session = Depends(get_db)):
    return crud_allergy.get_patient_allergy(db, patient_id)

@router.post("/Allergy/add", response_model=PatientAllergy)
def create_allergy(allergy: PatientAllergyCreate, db: Session = Depends(get_db)):
    return crud_allergy.create_allergy(db, allergy)

@router.delete("/Allergy/delete", response_model=PatientAllergy)
def delete_allergy(allergy_id: int, allergy: PatientAllergyUpdate, db: Session = Depends(get_db)):
    db_allergy = crud_allergy.delete_allergy(db, allergy_id, allergy)
    if not db_allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    return db_allergy
