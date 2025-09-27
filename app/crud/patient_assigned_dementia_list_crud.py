from sqlalchemy.orm import Session
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_list import (
    PatientAssignedDementiaListCreate,
    PatientAssignedDementiaListUpdate,
)
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

# Get all dementia list entries
def get_all_dementia_list_entries(db: Session):
    return (
        db.query(PatientAssignedDementiaList)
        .all()
    )

# Get a single dementia list entry by ID
def get_dementia_list_entry_by_id(db: Session, dementia_list_id: int):
    return db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.DementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.isDeleted == "0",
    ).first()

# Create a new dementia list entry
def create_dementia_list_entry(db: Session, dementia_list_data: PatientAssignedDementiaListCreate, created_by: str, user_full_name:str):
    new_entry = PatientAssignedDementiaList(
        **dementia_list_data.model_dump(),
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    updated_data_dict = serialize_data(dementia_list_data.model_dump())
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created patient assigned dementia",
        table="PatientAssignedDementiaList",
        entity_id=new_entry.DementiaTypeListId,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return new_entry

# Update a dementia list entry
def update_dementia_list_entry(
    db: Session, dementia_list_id: int, dementia_list_data: PatientAssignedDementiaListUpdate, modified_by: str, user_full_name:str
):
    db_entry = db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.DementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.IsDeleted == "0",
    ).first()

    if db_entry:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in dementia_list_data.model_dump(exclude_unset=True).items():
            setattr(db_entry, key, value)

        # Update timestamps and modifiedById
        db_entry.ModifiedDate = datetime.now()
        db_entry.ModifiedById = modified_by

        db.commit()
        db.refresh(db_entry)

        updated_data_dict = serialize_data(dementia_list_data.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated patient assigned dementia",
            table="PatientAssignedDementiaList",
            entity_id=dementia_list_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        return db_entry
    return None

# Soft delete a dementia list entry (set isDeleted to '1')
def delete_dementia_list_entry(db: Session, dementia_list_id: int, modified_by: str, user_full_name:str):
    db_entry = db.query(PatientAssignedDementiaList).filter(
        PatientAssignedDementiaList.DementiaTypeListId == dementia_list_id,
        PatientAssignedDementiaList.IsDeleted == "0",
    ).first()

    if db_entry:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
    
        # Soft delete the entry
        db_entry.IsDeleted = "1"
        db_entry.ModifiedDate = datetime.now()
        db_entry.ModifiedById = modified_by

        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Deleted patient assigned dementia",
            table="PatientAssignedDementiaList",
            entity_id=dementia_list_id,
            original_data=original_data_dict,
            updated_data=None,
        )
        return db_entry
    return None
