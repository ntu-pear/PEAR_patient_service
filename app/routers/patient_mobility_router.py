from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_mobility_list_crud as crud_mobility_list, patient_mobility_list_crud as crud_mobility
from ..schemas import patient_mobility_mapping as schemas_mobility
from ..schemas import patient_mobility_list as schemas_mobility_list

router = APIRouter()

# Routes for PATIENT_MOBILITY_LIST

# Get all mobility list entries
@router.get("/Mobility/List", response_model=list[schemas_mobility_list.PatientMobilityList])
def get_all_mobility_lists(db: Session = Depends(get_db)):
    return crud_mobility_list.get_all_mobility_list_entries(db)

# Get a single mobility list entry by ID
@router.get("/Mobility/List/{mobility_list_id}", response_model=schemas_mobility_list.PatientMobilityList)
def get_mobility_list_by_id(mobility_list_id: int, db: Session = Depends(get_db)):
    mobility_list = crud_mobility_list.get_mobility_list_entry_by_id(db, mobility_list_id)
    if not mobility_list:
        raise HTTPException(status_code=404, detail="Mobility list entry not found")
    return mobility_list

# Create a new mobility list entry
@router.post("/Mobility/List", response_model=schemas_mobility_list.PatientMobilityList)
def create_mobility_list_entry(mobility_list: schemas_mobility_list.PatientMobilityListCreate, db: Session = Depends(get_db)):
    return crud_mobility_list.create_mobility_list_entry(db, mobility_list, created_by="1")  # Replace 1 with dynamic user ID if needed

# Update a mobility list entry
@router.put("/Mobility/List/{mobility_list_id}", response_model=schemas_mobility_list.PatientMobilityList)
def update_mobility_list_entry(mobility_list_id: int, mobility_list: schemas_mobility_list.PatientMobilityListUpdate, db: Session = Depends(get_db)):
    updated_entry = crud_mobility_list.update_mobility_list_entry(db, mobility_list_id, mobility_list, modified_by="1")  # Replace 1 with dynamic user ID if needed
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Mobility list entry not found")
    return updated_entry

# Soft delete a mobility list entry
@router.delete("/Mobility/List/delete/{mobility_list_id}", response_model=schemas_mobility_list.PatientMobilityList)
def delete_mobility_list_entry(mobility_list_id: int, db: Session = Depends(get_db)):
    deleted_entry = crud_mobility_list.delete_mobility_list_entry(db, mobility_list_id, modified_by="1")  # Replace 1 with dynamic user ID if needed
    if not deleted_entry:
        raise HTTPException(status_code=404, detail="Mobility list entry not found")
    return deleted_entry
