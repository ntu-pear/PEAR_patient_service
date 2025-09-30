from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_prescription_list_crud as crud_prescription_list
from ..database import get_db
from ..schemas.patient_prescription_list import (
    PatientPrescriptionList,
    PatientPrescriptionListCreate,
    PatientPrescriptionListUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()

# Get all prescription list items (paginated)
@router.get("/PrescriptionList", response_model=PaginatedResponse[PatientPrescriptionList])
def get_prescription_lists(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_prescription_lists, totalRecords, totalPages = crud_prescription_list.get_prescription_lists(
        db, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    prescription_lists = [PatientPrescriptionList.model_validate(p) for p in db_prescription_lists]
    return PaginatedResponse(
        data=prescription_lists,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get a single prescription list item by ID
@router.get("/PrescriptionList/{prescription_list_id}", response_model=SingleResponse[PatientPrescriptionList])
def get_prescription_list(
    request: Request,
    prescription_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    db_prescription_list = crud_prescription_list.get_prescription_list_by_id(db, prescription_list_id)
    if not db_prescription_list:
        raise HTTPException(status_code=404, detail="Prescription list item not found")

    prescription_list = PatientPrescriptionList.model_validate(db_prescription_list)
    return SingleResponse(data=prescription_list)

# Create a new prescription list item
@router.post("/PrescriptionList/add", response_model=SingleResponse[PatientPrescriptionList])
def create_prescription_list(
    request: Request,
    prescription_list: PatientPrescriptionListCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription_list = crud_prescription_list.create_prescription_list(
        db, 
        prescription_list, 
        user_id, 
        user_full_name
    )
    prescription_list_response = PatientPrescriptionList.model_validate(db_prescription_list)
    return SingleResponse(data=prescription_list_response)

# Update an existing prescription list item
@router.put("/PrescriptionList/update/{prescription_list_id}", response_model=SingleResponse[PatientPrescriptionList])
def update_prescription_list(
    request: Request,
    prescription_list_id: int,
    prescription_list: PatientPrescriptionListUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription_list = crud_prescription_list.update_prescription_list(
        db, 
        prescription_list_id, 
        prescription_list, 
        user_id, 
        user_full_name
    )
    if not db_prescription_list:
        raise HTTPException(status_code=404, detail="Prescription list item not found")

    prescription_list_response = PatientPrescriptionList.model_validate(db_prescription_list)
    return SingleResponse(data=prescription_list_response)

# Soft delete a prescription list item
@router.delete("/PrescriptionList/delete/{prescription_list_id}", response_model=SingleResponse[PatientPrescriptionList])
def delete_prescription_list(
    request: Request,
    prescription_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_prescription_list = crud_prescription_list.delete_prescription_list(
        db, 
        prescription_list_id, 
        user_id, 
        user_full_name
    )
    if not db_prescription_list:
        raise HTTPException(status_code=404, detail="Prescription list item not found")

    prescription_list_response = PatientPrescriptionList.model_validate(db_prescription_list)
    return SingleResponse(data=prescription_list_response)