from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_assigned_dementia_mapping_crud as crud_assigned_dementia
from ..schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementia,
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaCreateResp,
    PatientAssignedDementiaUpdate,
)
from ..schemas.response import PaginatedResponse
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name


router = APIRouter()

@router.get(
    "/AllPatientAssignedDementia",
    response_model=PaginatedResponse[PatientAssignedDementia],
    description="Retrieve paginated assigned dementia entries for all patients."
)
def get_all_assigned_dementias(
    request: Request,
    db: Session = Depends(get_db),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    assignments, totalRecords, totalPages = crud_assigned_dementia.get_all_assigned_dementias(db, pageNo, pageSize)

    if not assignments:
        raise HTTPException(status_code=404, detail="No assigned dementias found")

    return PaginatedResponse(
        data=assignments,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

@router.get(
    "/PatientAssignedDementia/Patient/{patient_id}",
    response_model=PaginatedResponse[PatientAssignedDementia],
    description="Get paginated assigned dementias by patient ID."
)
def get_assigned_dementias(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    pageNo: int = Query(0, description="Page number (starting from 0)"),
    pageSize: int = Query(10, description="Number of records per page"),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    assignments, totalRecords, totalPages = crud_assigned_dementia.get_assigned_dementias(db, patient_id, pageNo, pageSize)

    if not assignments:
        raise HTTPException(status_code=404, detail=f"No assigned dementias found for patient with ID {patient_id}")

    return PaginatedResponse(
        data=assignments,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )


@router.get("/PatientAssignedDementia/Dementia/{assigned_dementia_id}", response_model=PatientAssignedDementia, description="Get a single assigned dementia by DementiaTypeListId.")
def get_assigned_dementia_by_dementia_id(request: Request, dementia_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    result = crud_assigned_dementia.get_assigned_dementia_by_dementia_id(db, dementia_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Assigned dementia with DementiaTypeListId {dementia_id} not found")

    return result


@router.post("/PatientAssignedDementia/add", response_model=PatientAssignedDementiaCreateResp, description="Create a new assigned dementia record.")
def create_assigned_dementia(request: Request,assigned_dementia_data: PatientAssignedDementiaCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    return crud_assigned_dementia.create_assigned_dementia(db, assigned_dementia_data, user_id, user_full_name)

@router.put("/PatientAssignedDementia/update/{assigned_dementia_id}", response_model=PatientAssignedDementiaCreateResp, description="Update an existing assigned dementia record.")
def update_assigned_dementia(request: Request,assigned_dementia_id: int, assigned_dementia_data: PatientAssignedDementiaUpdate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    result = crud_assigned_dementia.update_assigned_dementia(db, assigned_dementia_id, assigned_dementia_data, user_id, user_full_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Assigned dementia with ID {assigned_dementia_id} not found")
    return result

@router.delete("/PatientAssignedDementia/delete/{assigned_dementia_id}", response_model=PatientAssignedDementiaCreateResp, description="Soft delete an assigned dementia record by marking it as isDeleted.")
def delete_assigned_dementia(request: Request,assigned_dementia_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    result = crud_assigned_dementia.delete_assigned_dementia(db, assigned_dementia_id, user_id,user_full_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Assigned dementia with ID {assigned_dementia_id} not found")
    return result
