from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_crud as crud_patient
from ..schemas.response import SingleResponse, PaginatedResponse
from ..schemas.patient import (
    Patient,
    PatientCreate,
    PatientUpdate
)
router = APIRouter()

@router.get("/patients/{patient_id}", response_model=SingleResponse[Patient])
def read_patient(patient_id: int, db: Session = Depends(get_db), mask: bool = True):
    db_patient = crud_patient.get_patient(db=db, patient_id=patient_id, mask=mask)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data = patient)

@router.get("/patients/", response_model=PaginatedResponse[Patient])
def read_patients(mask: bool = True, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    patients, total = crud_patient.get_patients(db=db, skip=skip, limit=limit, mask=mask)
    patients = [Patient.model_validate(patient) for patient in patients]
    return PaginatedResponse(data=patients, skip= skip, limit=limit, totalRecords= total)

@router.post("/patients/", response_model=SingleResponse[Patient])
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud_patient.create_patient(db=db, patient=patient)
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/{patient_id}", response_model=SingleResponse[Patient])
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = crud_patient.update_patient(db=db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.delete("/patients/{patient_id}", response_model=SingleResponse[Patient])
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud_patient.delete_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)
