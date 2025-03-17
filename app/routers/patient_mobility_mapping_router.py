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
from ..schemas.response import SingleResponse, PaginatedResponse

router = APIRouter()

@router.get("/MobilityMapping/List", response_model=PaginatedResponse[PatientMobilityResponse])
def get_all_mobility_entries(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 10,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)

    mobility_entries, totalRecords, totalPages = patient_mobility_mapping_crud.get_all_mobility_entries(
        db=db,
        pageNo=pageNo,
        pageSize=pageSize
    )

    return PaginatedResponse(
        data=[PatientMobilityResponse.model_validate(entry) for entry in mobility_entries],
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

# Get paginated mobility entries for a specific patient
@router.get("/MobilityMapping/List/Patient/{patient_id}", response_model=PaginatedResponse[PatientMobilityResponse])
def get_mobility_entries_by_patient_id(
    request: Request,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 10,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)

    mobility_entries, totalRecords, totalPages = patient_mobility_mapping_crud.get_mobility_entries_by_patient_id(
        db=db,
        patient_id=patient_id,
        pageNo=pageNo,
        pageSize=pageSize
    )

    return PaginatedResponse(
        data=[PatientMobilityResponse.model_validate(entry) for entry in mobility_entries],
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

@router.get("/MobilityMapping/List/Mobility/{mobility_id}", response_model=list[PatientMobilityResponse])
def get_mobility_entry_by_mobility_id(request: Request, mobility_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    
    # Fetch mobility entries
    db_entries = patient_mobility_mapping_crud.get_mobility_entry_by_mobility_id(db, mobility_id)

    # Ensure it always returns a list
    if isinstance(db_entries, list):
        return db_entries
    elif db_entries is not None:
        return [db_entries]  # Wrap single object in a list
    else:
        return []  # Return an empty list if no results
    
@router.post("/MobilityMapping/List/add", response_model=PatientMobilityResponse)
def create_mobility_entry(
    request: Request, mobility_data: PatientMobilityCreate, db: Session = Depends(get_db), require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return patient_mobility_mapping_crud.create_mobility_entry(db, mobility_data, user_id, user_full_name)

@router.put("/MobilityMapping/List/update/{mobility_id}", response_model=PatientMobilityResponse)
def update_mobility_entry(
    request: Request,
    mobility_id: int,
    mobility_data: PatientMobilityUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return patient_mobility_mapping_crud.update_mobility_entry(
        db, mobility_id, mobility_data, user_id, user_full_name
    )

@router.delete("/MobilityMapping/List/delete/{mobility_id}", response_model=PatientMobilityResponse)
def delete_mobility_entry(request: Request, mobility_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return patient_mobility_mapping_crud.delete_mobility_entry(db, mobility_id, user_id, user_full_name)
