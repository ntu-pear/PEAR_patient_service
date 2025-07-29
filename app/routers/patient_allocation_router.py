from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..crud import patient_allocation_crud as crud
from ..schemas.patient_allocation import (
    PatientAllocation,
    PatientAllocationCreate,
    PatientAllocationUpdate
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name, get_role_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/allocation/{allocation_id}", response_model=PatientAllocation)
def get_allocation(
    allocation_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get a specific allocation by ID"""
    _ = extract_jwt_payload(request)
    db_allocation = crud.get_allocation_by_id(db, allocation_id)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.get("/allocation/patient/{patient_id}", response_model=PatientAllocation)
def get_patient_allocation(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """Get allocation for a specific patient"""
    _ = extract_jwt_payload(request, require_auth)
    db_allocation = crud.get_allocation_by_patient(db, patient_id)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found for this patient")
    return db_allocation

@router.get("/allocations/", response_model=List[PatientAllocation])
def get_allocations(
    request: Request,
    skip: int = Query(0, description="Skip first N records"),
    limit: int = Query(100, description="Limit the number of records returned"),
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    """Get all allocations with pagination"""
    _ = extract_jwt_payload(request, require_auth)
    return crud.get_all_allocations(db, skip=skip, limit=limit)

@router.post("/allocation/", response_model=PatientAllocation)
def create_allocation(
    allocation: PatientAllocationCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new allocation"""
    payload = extract_jwt_payload(request)
    user_id = get_user_id(payload) or "anonymous"
    role_name = get_role_name(payload)
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    # Only supervisors can create allocations
    if role_name != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Only supervisors can create allocations")
    
    # Check if patient already has an allocation
    existing_allocation = crud.get_allocation_by_patient(db, allocation.patientId)
    if existing_allocation:
        raise HTTPException(status_code=400, detail="Patient already has an allocation")
    return crud.create_allocation(db, allocation, user_id, user_full_name)


@router.put("/allocation/{allocation_id}", response_model=PatientAllocation)
def update_allocation(
    allocation_id: int,
    allocation: PatientAllocationUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update an existing allocation"""
    payload = extract_jwt_payload(request)
    user_id = get_user_id(payload) or "anonymous"
    role_name = get_role_name(payload)
    
    # Only supervisors can update allocations
    if role_name != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Only supervisors can update allocations")
    
    db_allocation = crud.update_allocation(db, allocation_id, allocation, user_id)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.delete("/allocation/{allocation_id}", response_model=PatientAllocation)
def delete_allocation(
    allocation_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Soft delete an allocation"""
    payload = extract_jwt_payload(request)
    user_id = get_user_id(payload) or "anonymous"
    role_name = get_role_name(payload)
    
    # Only supervisors can delete allocations
    if role_name != "SUPERVISOR":
        raise HTTPException(status_code=403, detail="Only supervisors can delete allocations")
    
    db_allocation = crud.delete_allocation(db, allocation_id, user_id)
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation