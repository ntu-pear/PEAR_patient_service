from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityUpdate,
    PatientMobilityResponse,
)
from ..crud import patient_mobility_mapping_crud
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/MobilityMapping/List", response_model=list[PatientMobilityResponse])
def get_all_mobility_entries(request: Request, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)

    return patient_mobility_mapping_crud.get_all_mobility_entries(db)

@router.get("/MobilityMapping/List/{patient_id}", response_model=list[PatientMobilityResponse])
def get_mobility_entry(request: Request, patient_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    
    return patient_mobility_mapping_crud.get_mobility_entries_by_id(db, patient_id)

@router.post("/MobilityMapping/List", response_model=PatientMobilityResponse)
def create_mobility_entry(
    request: Request, mobility_data: PatientMobilityCreate, db: Session = Depends(get_db), require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return patient_mobility_mapping_crud.create_mobility_entry(db, mobility_data, user_id, user_full_name)

@router.put("MobilityMapping/List/{patient_id}", response_model=PatientMobilityResponse)
def update_mobility_entry(
    request: Request,
    patient_id: int,
    mobility_data: PatientMobilityUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return patient_mobility_mapping_crud.update_mobility_entry(
        db, patient_id, mobility_data, user_id, user_full_name
    )

@router.delete("/MobilityMapping/List/{patient_id}", response_model=PatientMobilityResponse)
def delete_mobility_entry(request: Request, patient_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return patient_mobility_mapping_crud.delete_mobility_entry(db, patient_id, user_id, user_full_name)
