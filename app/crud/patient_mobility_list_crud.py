from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from ..models.patient_mobility_list_model import PatientMobilityList
from ..models.patient_mobility_mapping_model import PatientMobility
from ..schemas.patient_mobility_list import (
    PatientMobilityListCreate,
    PatientMobilityListUpdate,
)
from ..schemas.patient_mobility_mapping import (
    PatientMobilityCreate,
    PatientMobilityUpdate,
)

# CRUD for PATIENT_MOBILITY_LIST

# Get all mobility list entries
def get_all_mobility_list_entries(db: Session):
    try:
        entries = db.query(PatientMobilityList).filter(PatientMobilityList.IsDeleted == "0").all()
        if not entries:
            raise HTTPException(status_code=404, detail="No mobility list entries found.")
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying mobility list: {str(e)}")


# Get a single mobility list entry by ID
def get_mobility_list_entry_by_id(db: Session, mobility_list_id: int):
    entry = db.query(PatientMobilityList).filter(
        PatientMobilityList.MobilityListId == mobility_list_id,
        PatientMobilityList.IsDeleted == '0'
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Mobility list entry with ID {mobility_list_id} not found.")
    return entry

# Create a new mobility list entry
def create_mobility_list_entry(db: Session, mobility_list_data: PatientMobilityListCreate, created_by: int):
    new_entry = PatientMobilityList(
        **mobility_list_data.dict(exclude={"CreatedDateTime", "ModifiedDateTime", "CreatedById", "ModifiedById"}),  # Corrected set syntax
        CreatedDateTime=datetime.utcnow(),
        ModifiedDateTime=datetime.utcnow(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

# Update a mobility list entry
def update_mobility_list_entry(
    db: Session, mobility_list_id: int, mobility_list_data: PatientMobilityListUpdate, modified_by: int
):
    db_entry = db.query(PatientMobilityList).filter(
        PatientMobilityList.MobilityListId == mobility_list_id,
        PatientMobilityList.IsDeleted == '0',
    ).first()

    if db_entry:
        for key, value in mobility_list_data.dict(exclude={"MobilityListId"}).items():  # Exclude MobilityListId
            setattr(db_entry, key, value)

        db_entry.ModifiedDateTime = datetime.utcnow()
        db_entry.ModifiedById = modified_by

        db.commit()
        db.refresh(db_entry)
        return db_entry
    return None

# Soft delete a mobility list entry (set IsDeleted to '1')

def delete_mobility_list_entry(db: Session, mobility_list_id: int, modified_by: int):
    # Query for the entry to be deleted
    db_entry = db.query(PatientMobilityList).filter(
        PatientMobilityList.MobilityListId == mobility_list_id,
        PatientMobilityList.IsDeleted == "0"  # Use boolean False for filtering
    ).first()

    # Raise an exception if the entry is not found
    if not db_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Mobility list entry with ID {mobility_list_id} not found."
        )

    # Soft delete the entry by setting IsDeleted to True
    db_entry.IsDeleted = "1"  # Use boolean True
    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    # Commit the transaction to save the changes
    db.commit()
    db.refresh(db_entry)  # Refresh the entry to return the updated instance
    return db_entry
