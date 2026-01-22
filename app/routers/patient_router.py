from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_crud as crud_patient
from ..database import get_db
from ..schemas.patient import Patient, PatientCreate, PatientUpdate
from ..schemas.response import PaginatedResponse, SingleResponse

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
def read_patients(
    request: Request,
    name: Optional[str] = Query(None, description="Filter patients by name (non-exact match)", include_in_schema=True),
    isActive: Optional[str] = Query(None, description="Filter patients by isActive (0 or 1)", include_in_schema=True),
    require_auth: bool = Query(True, description="Require authentication"),
    mask: bool = Query(True, description="Mask sensitive data"),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    _ = extract_jwt_payload(request, require_auth)
    db_patients, totalRecords, totalPages = crud_patient.get_patients(db=db, pageNo=pageNo, pageSize=pageSize, mask=mask, name=name, isActive = isActive)
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(data=patients, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)

@router.get("/patients/by-doctor/{doctor_id}", response_model=PaginatedResponse[Patient])
def get_patients_by_doctor_id(
    doctor_id: str,
    request: Request,
    require_auth: bool = Query(True, description="Require authentication"),
    mask: bool = Query(True, description="Mask sensitive data"),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    """Get all patients allocated to a specific doctor"""
    _ = extract_jwt_payload(request, require_auth)
    
    db_patients, totalRecords, totalPages = crud_patient.get_patients_by_doctor(
        db=db, 
        doctor_id=doctor_id, 
        mask=mask, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(
        data=patients, 
        pageNo=pageNo, 
        pageSize=pageSize, 
        totalRecords=totalRecords, 
        totalPages=totalPages
    )


@router.get("/patients/by-supervisor/{supervisor_id}", response_model=PaginatedResponse[Patient])
def get_patients_by_supervisor_id(
    supervisor_id: str,
    request: Request,
    require_auth: bool = Query(True, description="Require authentication"),
    mask: bool = Query(True, description="Mask sensitive data"),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    """Get all patients allocated to a specific supervisor"""
    _ = extract_jwt_payload(request, require_auth)
    
    db_patients, totalRecords, totalPages = crud_patient.get_patients_by_supervisor(
        db=db, 
        supervisor_id=supervisor_id, 
        mask=mask, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(
        data=patients, 
        pageNo=pageNo, 
        pageSize=pageSize, 
        totalRecords=totalRecords, 
        totalPages=totalPages
    )
    
@router.get("/patients/by-caregiver/{caregiver_id}", response_model=PaginatedResponse[Patient])
def get_patients_by_caregiver_id(
    caregiver_id: str,
    request: Request,
    require_auth: bool = Query(True, description="Require authentication"),
    mask: bool = Query(True, description="Mask sensitive data"),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    """Get all patients allocated to a specific caregiver"""
    _ = extract_jwt_payload(request, require_auth)
    
    db_patients, totalRecords, totalPages = crud_patient.get_patients_by_caregiver(
        db=db, 
        caregiver_id=caregiver_id, 
        mask=mask, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(
        data=patients, 
        pageNo=pageNo, 
        pageSize=pageSize, 
        totalRecords=totalRecords, 
        totalPages=totalPages
    )

@router.get("/patients/by-guardian/{guardian_application_user_id}", response_model=PaginatedResponse[Patient])
def get_patients_by_guardian_application_user_id(
    guardian_application_user_id: str,
    request: Request,
    require_auth: bool = Query(True, description="Require authentication"),
    mask: bool = Query(True, description="Mask sensitive data"),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    db: Session = Depends(get_db),
):
    """Get all patients allocated to a specific guardian by their application user ID"""
    _ = extract_jwt_payload(request, require_auth)
    
    db_patients, totalRecords, totalPages = crud_patient.get_patients_by_guardian(
        db=db, 
        guardian_application_user_id=guardian_application_user_id, 
        mask=mask, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    patients = [Patient.model_validate(patient) for patient in db_patients]
    return PaginatedResponse(
        data=patients, 
        pageNo=pageNo, 
        pageSize=pageSize, 
        totalRecords=totalRecords, 
        totalPages=totalPages
    )

@router.post("/patients/add", response_model=SingleResponse[Patient])
def create_patient(patient: PatientCreate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.create_patient(db, patient, user_id, user_full_name)
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}", response_model=SingleResponse[Patient])
def update_patient(patient_id: int, patient: PatientUpdate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.update_patient(db, patient_id, patient, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.put("/patients/update/{patient_id}/update_patient_profile_picture", response_model=SingleResponse[Patient])
def update_patient_profile_picture(patient_id: int, request: Request, require_auth: bool = True, file: UploadFile = File(...), db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.update_patient_profile_picture(db, patient_id, file, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.delete("/patients/delete/{patient_id}", response_model=SingleResponse[Patient])
def delete_patient(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.delete_patient(db, patient_id, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)

@router.delete("/patients/update/{patient_id}/update_patient_profile_picture", response_model=SingleResponse[Patient])
def delete_patient_profile_picture(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "1"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_patient = crud_patient.delete_patient_profile_picture(db, patient_id, user_id, user_full_name)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient = Patient.model_validate(db_patient)
    return SingleResponse(data=patient)