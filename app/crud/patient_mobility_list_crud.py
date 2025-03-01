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
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

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
def create_mobility_list_entry(db: Session, mobility_list_data: PatientMobilityListCreate, created_by: str, user_full_name: str):
    new_entry = PatientMobilityList(
        **mobility_list_data.model_dump(exclude={"CreatedDateTime", "ModifiedDateTime", "CreatedById", "ModifiedById"}),  # Corrected set syntax
        CreatedDateTime=datetime.utcnow(),
        ModifiedDateTime=datetime.utcnow(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    updated_data_dict = serialize_data(mobility_list_data.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created mobility list entry",
        table="PatientMobilityList",
        entity_id=new_entry.MobilityListId,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return new_entry

# Update a mobility list entry
def update_mobility_list_entry(
    db: Session, mobility_list_id: int, mobility_list_data: PatientMobilityListUpdate, modified_by: str, user_full_name: str
):
    # Query the database for the entry to update
    db_entry = db.query(PatientMobilityList).filter(
        PatientMobilityList.MobilityListId == mobility_list_id,
        PatientMobilityList.IsDeleted == '0',  # Ensure the entry is not marked as deleted
    ).first()

    if not db_entry:
        # If the entry is not found, return None (or optionally raise an exception)
        return None

    # Update the fields of the entry
    update_data = mobility_list_data.model_dump(exclude={"MobilityListId"}, exclude_unset=True)

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    for key, value in update_data.items():
        setattr(db_entry, key, value)

    # Update the modified fields
    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    try:
        # Commit the transaction and refresh the entry
        db.commit()
        db.refresh(db_entry)

        updated_data_dict = serialize_data(mobility_list_data.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated mobility list entry",
            table="PatientMobilityList",
            entity_id=mobility_list_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise e

    return db_entry


# Soft delete a mobility list entry (set IsDeleted to '1')

def delete_mobility_list_entry(db: Session, mobility_list_id: int, modified_by: str, user_full_name: str):
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

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Soft delete the entry by setting IsDeleted to True
    db_entry.IsDeleted = "1"  # Use boolean True
    db_entry.ModifiedDateTime = datetime.utcnow()
    db_entry.ModifiedById = modified_by

    # Commit the transaction to save the changes
    db.commit()
    db.refresh(db_entry)  # Refresh the entry to return the updated instance

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Deleted mobility list entry",
        table="PatientMobilityList",
        entity_id=mobility_list_id,
        original_data=original_data_dict,
        updated_data=serialize_data(db_entry),
    )
    return db_entry
