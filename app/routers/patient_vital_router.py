import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.services.highlight_helper import create_highlight_if_needed

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_vital_crud as crud_vital
from ..database import get_db
from ..schemas.patient_vital import (
    PatientVital,
    PatientVitalCreate,
    PatientVitalDelete,
    PatientVitalUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()

# Get the latest vital record for a patient
@router.get("/Vital", response_model=SingleResponse[PatientVital])
def get_latest_vital(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)  # You can also capture the user, if needed
    db_vital = crud_vital.get_latest_vital(db, patient_id)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")

    vital = PatientVital.model_validate(db_vital)
    return SingleResponse(data=vital)

# Get a paginated list of vital records for a patient
@router.get("/Vital/list", response_model=PaginatedResponse[PatientVital])
def get_vital_list(
    request: Request,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    vitals, totalRecords, totalPages = crud_vital.get_vital_list(
        db=db,
        patient_id=patient_id,
        pageNo=pageNo,
        pageSize=pageSize
    )
    vitals = [PatientVital.model_validate(vital) for vital in vitals]
    return PaginatedResponse(
        data=vitals,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Create a new vital record
@router.post("/Vital/add", response_model=SingleResponse[PatientVital])
def create_vital(
    request: Request,
    vital: PatientVitalCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_vital = crud_vital.create_vital(db, vital, user_id, user_full_name)
    vital_data = PatientVital.model_validate(db_vital)
    
    return SingleResponse(data=vital_data)

# Update an existing vital record
@router.put("/Vital/update/{vital_id}", response_model=SingleResponse[PatientVital])
def update_vital(
    request: Request,
    vital_id: int,
    vital: PatientVitalUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_vital = crud_vital.update_vital(db, vital_id, vital, user_id, user_full_name)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")

    vital_data = PatientVital.model_validate(db_vital)
    
    # Calling Highlight function to see if a highlight needs to be created
    create_highlight_if_needed(
        db=db,
        source_record=vital_data,
        type_code="VITAL",
        patient_id=vital_data.PatientId,
        source_table="VITAL",
        created_by=user_id
    )
    
    
    return SingleResponse(data=vital_data)

# Soft delete a vital record
@router.delete("/Vital/delete", response_model=SingleResponse[PatientVital])
def delete_vital(
    request: Request,
    vital: PatientVitalDelete,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_vital = crud_vital.delete_vital(db, vital.Id, user_id, user_full_name)
    if not db_vital:
        raise HTTPException(status_code=404, detail="Vital record not found")

    vital_data = PatientVital.model_validate(db_vital)
    return SingleResponse(data=vital_data)
