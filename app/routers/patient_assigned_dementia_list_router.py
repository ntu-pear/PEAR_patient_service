from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..crud import patient_assigned_dementia_list_crud as crud_dementia_list
from ..schemas.patient_assigned_dementia_list import (
    PatientAssignedDementiaListCreate,
    PatientAssignedDementiaListUpdate,
    PatientAssignedDementiaListRead,
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name

router = APIRouter()

# Get all dementia list entries
@router.get("/PatientAssignedDementiaList", response_model=list[PatientAssignedDementiaListRead])
def get_dementia_list_entries(request: Request, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    entries = crud_dementia_list.get_all_dementia_list_entries(db)
    if not entries:
        raise HTTPException(status_code=404, detail="No dementia list entries found")
    return entries

# Get a single dementia list entry by ID
@router.get("/PatientAssignedDementiaList/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def get_dementia_list_entry(request: Request,dementia_list_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    _ = extract_jwt_payload(request, require_auth)
    db_entry = crud_dementia_list.get_dementia_list_entry_by_id(db, dementia_list_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry

# Create a new dementia list entry
@router.post("/PatientAssignedDementiaList", response_model=PatientAssignedDementiaListRead)
def create_dementia_list_entry(
    request: Request,dementia_list_data: PatientAssignedDementiaListCreate, db: Session = Depends(get_db), require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    try:
        return crud_dementia_list.create_dementia_list_entry(db, dementia_list_data, user_id, user_full_name)
    except Exception as e:
        print(dementia_list_data)

        raise HTTPException(status_code=400, detail=f"Error creating dementia list entry: {e}")

# Update a dementia list entry
@router.put("/PatientAssignedDementiaList/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def update_dementia_list_entry(
    request: Request,
    dementia_list_id: int,
    dementia_list_data: PatientAssignedDementiaListUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_entry = crud_dementia_list.update_dementia_list_entry(db, dementia_list_id, dementia_list_data, user_id, user_full_name)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry

# Soft delete a dementia list entry (set isDeleted to '1')
@router.delete("/PatientAssignedDementiaList/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def delete_dementia_list_entry(request: Request,dementia_list_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    # Replace `modified_by` with the current user ID in a real-world scenario
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_entry = crud_dementia_list.delete_dementia_list_entry(db, dementia_list_id, user_id, user_full_name)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry
