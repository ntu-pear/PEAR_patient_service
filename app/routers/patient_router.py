from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_crud as crud_patient
from ..schemas.response import SingleResponse, PaginatedResponse
from ..schemas.patient import (
    Patient,
    PatientCreate,
    PatientUpdate
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name

router = APIRouter()

@router.get("/patients/{patient_id}", response_model=SingleResponse[Patient])
def read_patient(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db), mask: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    db_patient = crud_patient.get_patient(db=db, patient_id=patient_id, mask=mask)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data = patient)

@router.get("/patients/", response_model=PaginatedResponse[Patient])
def read_patients(request: Request, require_auth: bool = True, mask: bool = True, pageNo: int = 0, pageSize: int = 10, db: Session = Depends(get_db)):
    _ = extract_jwt_payload(request, require_auth)
    db_patients, totalRecords, totalPages = crud_patient.get_patients(db=db, pageNo=pageNo, pageSize=pageSize, mask=mask)
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(data=patients, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)

@router.post("/patients/add", response_model=SingleResponse[Patient])
def create_patient(patient: PatientCreate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.create_patient(db, patient, user_id, user_full_name)
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}", response_model=SingleResponse[Patient])
def update_patient(patient_id: int, patient: PatientUpdate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.update_patient(db, patient_id, patient, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}/update_patient_profile_picture", response_model=SingleResponse[Patient])
def update_patient_profile_picture(patient_id: int, request: Request, require_auth: bool = True, file: UploadFile = File(...), db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.update_patient_profile_picture(db, patient_id, file, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)


@router.delete("/patients/delete/{patient_id}", response_model=SingleResponse[Patient])
def delete_patient(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.delete_patient(db, patient_id, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)
