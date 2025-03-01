from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_prescription_crud as crud_prescription
from ..schemas.patient_prescription import (
    PatientPrescription,
    PatientPrescriptionCreate,
    PatientPrescriptionUpdate
)
from ..schemas.response import SingleResponse, PaginatedResponse
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name

router = APIRouter()

# Get all prescriptions (paginated)
@router.get("/Prescription", response_model=PaginatedResponse[PatientPrescription])
def get_prescriptions(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_prescriptions, totalRecords, totalPages = crud_prescription.get_prescriptions(db, pageNo=pageNo, pageSize=pageSize)
    patient_prescriptions = [PatientPrescription.model_validate(p) for p in db_prescriptions]
    return PaginatedResponse(
        data=patient_prescriptions,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get all prescriptions for a single patient (paginated)
@router.get("/Prescription/PatientPrescription", response_model=PaginatedResponse[PatientPrescription])
def get_patient_prescriptions(
    request: Request,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_prescriptions, totalRecords, totalPages = crud_prescription.get_patient_prescriptions(
        db,
        patient_id,
        pageNo=pageNo,
        pageSize=pageSize
    )
    patient_prescriptions = [PatientPrescription.model_validate(p) for p in db_prescriptions]
    return PaginatedResponse(
        data=patient_prescriptions,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get a single prescription by ID
@router.get("/Prescription/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def get_prescription(
    request: Request,
    prescription_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_prescription = crud_prescription.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)

# Create a new prescription
@router.post("/Prescription/add", response_model=SingleResponse[PatientPrescription])
def create_prescription(
    request: Request,
    prescription: PatientPrescriptionCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription = crud_prescription.create_prescription(db, prescription, user_id, user_full_name)
    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)

# Update an existing prescription
@router.put("/Prescription/update/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def update_prescription(
    request: Request,
    prescription_id: int,
    prescription: PatientPrescriptionUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription = crud_prescription.update_prescription(db, prescription_id, prescription, user_id, user_full_name)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)

# Soft delete a prescription
@router.delete("/Prescription/delete/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def delete_prescription(
    request: Request,
    prescription_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription = crud_prescription.delete_prescription(db, prescription_id, user_id, user_full_name)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)
