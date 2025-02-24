from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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
def read_patients(mask: bool = True, pageNo: int = 0, pageSize: int = 10, db: Session = Depends(get_db)):
    db_patients, totalRecords, totalPages = crud_patient.get_patients(db=db, pageNo=pageNo, pageSize=pageSize, mask=mask)
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(data=patients, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)

@router.post("/patients/add", response_model=SingleResponse[Patient])
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud_patient.create_patient(db=db, patient=patient)
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}", response_model=SingleResponse[Patient])
def update_patient(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db)):
    db_patient = crud_patient.update_patient(db=db, patient_id=patient_id, patient=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}/update_patient_profile_picture", response_model=SingleResponse[Patient])
def update_patient_profile_picture(patient_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_patient = crud_patient.update_patient_profile_picture(db=db, patient_id=patient_id, file=file)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)


@router.delete("/patients/delete/{patient_id}", response_model=SingleResponse[Patient])
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud_patient.delete_patient(db=db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)
