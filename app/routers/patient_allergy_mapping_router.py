from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_allergy_mapping_crud
from ..schemas.patient_allergy_mapping import PatientAllergy, PatientAllergyCreate,PatientAllergyCreateResp,PatientAllergyUpdateReq

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

@router.post("/create_patient_allergy", response_model=PatientAllergyCreateResp, description="Create a new patient allergy record.")
def create_patient_allergy(allergy_data: PatientAllergyCreate, db: Session = Depends(get_db)):
    
    # TODO: CHANGE USER ID to the actual user ID
    userId = 1
    
    return patient_allergy_mapping_crud.create_patient_allergy(db, allergy_data, userId)

@router.put("/update_patient_allergy/{patient_id}", response_model=PatientAllergyCreateResp, description="Update an existing patient allergy record. Patient_AllergyID is the key of the patient allergy record itself.")
def update_patient_allergy(patient_id:int, allergy_data: PatientAllergyUpdateReq, db: Session = Depends(get_db)):
    
    # TODO: Replace with the actual user ID
    userId = 1
    
    return patient_allergy_mapping_crud.update_patient_allergy(db, patient_id, allergy_data, userId)

@router.delete("/delete_patient_allergy/{patient_allergy_id}", response_model=PatientAllergyCreateResp, description="Soft delete a patient allergy record by marking it as inactive.")
def delete_patient_allergy(patient_allergy_id: int, db: Session = Depends(get_db)):
    # TODO: Replace with the actual user ID
    userId = 1
    
    return patient_allergy_mapping_crud.delete_patient_allergy(db, patient_allergy_id, userId)
