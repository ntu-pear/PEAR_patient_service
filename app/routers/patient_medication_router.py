from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_medication_crud as crud_medication
from ..schemas.patient_medication import (
    PatientMedication,
    PatientMedicationCreate,
    PatientMedicationUpdate
)
from ..schemas.response import SingleResponse, PaginatedResponse
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name

router = APIRouter()

# Get all medications (paginated)
@router.get("/Medication", response_model=PaginatedResponse[PatientMedication])
def get_medications(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_medications, totalRecords, totalPages = crud_medication.get_medications(db, pageNo=pageNo, pageSize=pageSize)
    patient_medications = [PatientMedication.model_validate(p) for p in db_medications]
    return PaginatedResponse(
        data=patient_medications,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get all medications for a single patient (paginated)
@router.get("/Medication/PatientMedication", response_model=PaginatedResponse[PatientMedication])
def get_patient_medications(
    request: Request,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_medications, totalRecords, totalPages = crud_medication.get_patient_medications(
        db,
        patient_id,
        pageNo=pageNo,
        pageSize=pageSize
    )
    patient_medications = [PatientMedication.model_validate(p) for p in db_medications]
    return PaginatedResponse(
        data=patient_medications,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get a single medication by ID
@router.get("/Medication/{medication_id}", response_model=SingleResponse[PatientMedication])
def get_medication(
    request: Request,
    medication_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_medication = crud_medication.get_medication(db, medication_id)
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    patient_medication = PatientMedication.model_validate(db_medication)
    return SingleResponse(data=patient_medication)

# Create a new medication
@router.post("/Medication/add", response_model=SingleResponse[PatientMedication])
def create_medication(
    request: Request,
    medication: PatientMedicationCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_medication = crud_medication.create_medication(db, medication, user_id, user_full_name)
    patient_medication = PatientMedication.model_validate(db_medication)
    return SingleResponse(data=patient_medication)

# Update an existing medication
@router.put("/Medication/update/{medication_id}", response_model=SingleResponse[PatientMedication])
def update_medication(
    request: Request,
    medication_id: int,
    medication: PatientMedicationUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_medication = crud_medication.update_medication(db, medication_id, medication, user_id, user_full_name)
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    patient_medication = PatientMedication.model_validate(db_medication)
    return SingleResponse(data=patient_medication)

# Soft delete a medication
@router.delete("/Medication/delete/{medication_id}", response_model=SingleResponse[PatientMedication])
def delete_medication(
    request: Request,
    medication_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_medication = crud_medication.delete_medication(db, medication_id, user_id, user_full_name)
    if not db_medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    patient_medication = PatientMedication.model_validate(db_medication)
    return SingleResponse(data=patient_medication)
