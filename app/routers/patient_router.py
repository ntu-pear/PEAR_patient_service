from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_crud as crud_patient
from ..schemas import patient as schemas_patient
from ..schemas import patient_patient_list_language as ppll


router = APIRouter()

@router.post("/patients/", response_model=schemas_patient.Patient)
def create_patient(patient: schemas_patient.PatientCreate, db: Session = Depends(get_db)):
    return crud_patient.create_patient(db=db, patient=patient)

# local test api
@router.post("/patients/test", response_model=ppll.Patient_PatientListLanguage)
def test(patient_language: schemas_patient.PatientLanguageCreate, db: Session = Depends(get_db)):
    language_create = crud_patient.create_patient_language(db=db, patient_language=patient_language)
    
    if language_create is None:
        raise HTTPException(status_code=404, detail="Language does not exist in the patient_list_language table.")
    
    return language_create

@router.get("/patients/{patient_id}", response_model=schemas_patient.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.get("/patients/", response_model=list[schemas_patient.Patient])
def read_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    patients = crud_patient.get_patients(db=db, skip=skip, limit=limit)
    return patients

@router.put("/patients/{patient_id}", response_model=schemas_patient.Patient)
def update_patient(patient_id: int, patient: schemas_patient.PatientUpdate, db: Session = Depends(get_db)):
    db_patient = crud_patient.update_patient(db=db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.delete("/patients/{patient_id}", response_model=schemas_patient.Patient)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud_patient.delete_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient
