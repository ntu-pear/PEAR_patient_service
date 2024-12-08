from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..crud import patient_assigned_dementia_list_crud as crud_dementia_list
from ..schemas.patient_assigned_dementia_list import (
    PatientAssignedDementiaListCreate,
    PatientAssignedDementiaListUpdate,
    PatientAssignedDementiaListRead,
)

router = APIRouter()

# Get all dementia list entries
@router.get("/PatientAssignedDementiaList", response_model=list[PatientAssignedDementiaListRead])
def get_dementia_list_entries(db: Session = Depends(get_db)):
    entries = crud_dementia_list.get_all_dementia_list_entries(db)
    if not entries:
        raise HTTPException(status_code=404, detail="No dementia list entries found")
    return entries

# Get a single dementia list entry by ID
@router.get("/PatientAssignedDementiaList/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def get_dementia_list_entry(dementia_list_id: int, db: Session = Depends(get_db)):
    db_entry = crud_dementia_list.get_dementia_list_entry_by_id(db, dementia_list_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry

# Create a new dementia list entry
@router.post("/PatientAssignedDementiaList/add", response_model=PatientAssignedDementiaListRead)
def create_dementia_list_entry(
    dementia_list_data: PatientAssignedDementiaListCreate, db: Session = Depends(get_db)
):
    # Replace `created_by` with the current user ID in a real-world scenario
    created_by = 1
    try:
        return crud_dementia_list.create_dementia_list_entry(db, dementia_list_data, created_by)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating dementia list entry: {e}")

# Update a dementia list entry
@router.put("/PatientAssignedDementiaList/update/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def update_dementia_list_entry(
    dementia_list_id: int,
    dementia_list_data: PatientAssignedDementiaListUpdate,
    db: Session = Depends(get_db),
):
    # Replace `modified_by` with the current user ID in a real-world scenario
    modified_by = 1
    db_entry = crud_dementia_list.update_dementia_list_entry(db, dementia_list_id, dementia_list_data, modified_by)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry

# Soft delete a dementia list entry (set isDeleted to '1')
@router.put("/PatientAssignedDementiaList/delete/{dementia_list_id}", response_model=PatientAssignedDementiaListRead)
def delete_dementia_list_entry(dementia_list_id: int, db: Session = Depends(get_db)):
    # Replace `modified_by` with the current user ID in a real-world scenario
    modified_by = 1
    db_entry = crud_dementia_list.delete_dementia_list_entry(db, dementia_list_id, modified_by)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Dementia list entry not found")
    return db_entry
