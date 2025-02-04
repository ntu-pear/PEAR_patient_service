from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_crud as crud_patient
from ..schemas import patient as schemas_patient
from ..schemas.patient import (
    Patient,
    PatientCreate,
    PatientUpdate
)
router = APIRouter()

@router.get("/patients/{patient_id}", response_model=Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db), mask: bool = True):
    db_patient = crud_patient.get_patient(db=db, patient_id=patient_id, mask=mask)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.get("/patients/", response_model=list[Patient])
def read_patients(mask: bool = True, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    patients = crud_patient.get_patients(db=db, skip=skip, limit=limit, mask=mask)
    return patients

@router.post("/patients/", response_model=Patient)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    return crud_patient.create_patient(db=db, patient=patient)

@router.put("/patients/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = crud_patient.update_patient(db=db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/patients/{patient_id}", response_model=Patient)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud_patient.delete_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient
