from sqlalchemy.orm import Session
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_list import (
    PatientAssignedDementiaListCreate,
    PatientAssignedDementiaListUpdate,
)
from datetime import datetime


# Get all dementia list entries
def get_all_dementia_list_entries(db: Session):
    return (
        db.query(PatientAssignedDementiaList)
        .all()
    )
# Get a single dementia list entry by ID
def get_dementia_list_entry_by_id(db: Session, dementia_list_id: int):
    return db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.dementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.isDeleted == "0",
    ).first()


# Create a new dementia list entry
def create_dementia_list_entry(db: Session, dementia_list_data: PatientAssignedDementiaListCreate, created_by: int):
    new_entry = PatientAssignedDementiaList(
        **dementia_list_data.dict(),
        
        createdDate=datetime.utcnow(),
        modifiedDate=datetime.utcnow(),
        createdById=created_by,
        modifiedById=created_by,
        isDeleted="0",
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_list import PatientAssignedDementiaListCreate

def create_dementia_list_entry(
    db: Session, dementia_list_data: PatientAssignedDementiaListCreate, created_by: int
):
    try:
        # Prepare the data dictionary for the new entry
        new_entry_data = dementia_list_data.dict()
        new_entry_data.update({
            "createdDate": datetime.utcnow(),
            "modifiedDate": datetime.utcnow(),
            "isDeleted": "0",  # Ensure the entry is active upon creation
        })

        # Create the database model instance
        new_entry = PatientAssignedDementiaList(**new_entry_data)

        # Add and commit the new entry to the database
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return new_entry
    except Exception as e:
        db.rollback()  # Rollback in case of any errors
        raise HTTPException(status_code=500, detail=f"Error creating dementia list entry: {str(e)}")


# Update a dementia list entry
def update_dementia_list_entry(
    db: Session, dementia_list_id: int, dementia_list_data: PatientAssignedDementiaListUpdate, modified_by: int
):
    db_entry = db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.dementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.isDeleted == "0",
    ).first()

    if db_entry:
        for key, value in dementia_list_data.dict(exclude_unset=True).items():
            setattr(db_entry, key, value)

        # Update timestamps and modifiedById
        db_entry.modifiedDate = datetime.utcnow()
        db_entry.modifiedById = modified_by

        db.commit()
        db.refresh(db_entry)
        return db_entry
    return None


# Soft delete a dementia list entry (set isDeleted to '1')
def delete_dementia_list_entry(db: Session, dementia_list_id: int, modified_by: int):
    db_entry = db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.dementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.isDeleted == "0",
    ).first()

    if db_entry:
        # Soft delete the entry
        db_entry.isDeleted = "1"
        db_entry.modifiedDate = datetime.utcnow()
        db_entry.modifiedById = modified_by

        db.commit()
        return db_entry
    return None
