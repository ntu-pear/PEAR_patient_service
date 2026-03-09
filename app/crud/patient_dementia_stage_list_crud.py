from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from ..models.patient_dementia_stage_list_model import PatientDementiaStageList
from ..schemas.patient_dementia_stage_list import (
    PatientDementiaStageListCreate,
    PatientDementiaStageListUpdate,
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_dementia_stage_list_entries(db: Session):
    try:
        entries = db.query(PatientDementiaStageList).filter(
            PatientDementiaStageList.IsDeleted == "0"
        ).order_by(PatientDementiaStageList.DementiaStage.asc()).all()
        if not entries:
            raise HTTPException(status_code=404, detail="No dementia stage list entries found.")
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying dementia stage list: {str(e)}")

def get_dementia_stage_list_entry_by_id(db: Session, stage_id: int):
    entry = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.id == stage_id,
        PatientDementiaStageList.IsDeleted == '0'
    ).first()
    if not entry:
        raise HTTPException(
            status_code=404, 
            detail=f"Dementia stage list entry with ID {stage_id} not found."
        )
    return entry

def create_dementia_stage_list_entry(
    db: Session, 
    stage_data: PatientDementiaStageListCreate, 
    created_by: str, 
    user_full_name: str
):
    """Create a new dementia stage with duplicate check and uppercase transformation"""
    # Convert DementiaStage to UPPERCASE before checking and inserting
    uppercase_stage = stage_data.DementiaStage.upper()
    
    # Check if a stage with the same name already exists (case-insensitive)
    existing_stage = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.DementiaStage == uppercase_stage,
        PatientDementiaStageList.IsDeleted == "0"
    ).first()
    
    if existing_stage:
        raise HTTPException(
            status_code=400, 
            detail=f"Dementia stage '{uppercase_stage}' already exists."
        )
    
    new_entry = PatientDementiaStageList(
        DementiaStage=uppercase_stage,
        IsDeleted="0",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    
    updated_data_dict = serialize_data({"DementiaStage": uppercase_stage})
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    # Retrieve the name of the dementia stage
    dementia_stage_name = stage_data.DementiaStage if stage_data else None

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message=f"Created dementia stage: {dementia_stage_name}",
        table="PatientDementiaStageList",
        entity_id=new_entry.id,
        original_data=None,
        updated_data=updated_data_dict,
        log_type = "system",
        is_system_config=True
    )
    return new_entry

def update_dementia_stage_list_entry(
    db: Session, 
    stage_id: int, 
    stage_data: PatientDementiaStageListUpdate, 
    modified_by: str, 
    user_full_name: str
):
    """Update an existing dementia stage with uppercase transformation"""
    # Query the database for the entry to update
    db_entry = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.id == stage_id,
        PatientDementiaStageList.IsDeleted == '0',
    ).first()

    if not db_entry:
        return None

    # Convert DementiaStage to UPPERCASE if it's being updated
    if stage_data.DementiaStage:
        uppercase_stage = stage_data.DementiaStage.upper()
        
        # Check if updating to a stage name that already exists
        existing_stage = db.query(PatientDementiaStageList).filter(
            PatientDementiaStageList.DementiaStage == uppercase_stage,
            PatientDementiaStageList.id != stage_id,
            PatientDementiaStageList.IsDeleted == "0"
        ).first()
        
        if existing_stage:
            raise HTTPException(
                status_code=400, 
                detail=f"Dementia stage '{uppercase_stage}' already exists."
            )
    else:
        uppercase_stage = None

    # Update the fields of the entry
    update_data = stage_data.model_dump(exclude={"id"}, exclude_unset=True)
    if uppercase_stage:
        update_data["DementiaStage"] = uppercase_stage

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Store the old dementia stage for message field in log
    old_dementia_stage_name = db_entry.DementiaStage

    for key, value in update_data.items():
        setattr(db_entry, key, value)

    # Update the modified fields
    db_entry.ModifiedDate = datetime.now()
    db_entry.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_entry)

        updated_data_dict = serialize_data(update_data)
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Updated dementia stage - {old_dementia_stage_name} -> {db_entry.Value}",
            table="PatientDementiaStageList",
            entity_id=stage_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            log_type="system",
            is_system_config=True
        )
    except Exception as e:
        db.rollback()
        raise e

    return db_entry

# Soft delete a dementia stage list entry (set IsDeleted to '1')
def delete_dementia_stage_list_entry(
    db: Session, 
    stage_id: int, 
    modified_by: str, 
    user_full_name: str
):
    # Query for the entry to be deleted
    db_entry = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.id == stage_id,
        PatientDementiaStageList.IsDeleted == "0"
    ).first()

    # Raise an exception if the entry is not found
    if not db_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Dementia stage list entry with ID {stage_id} not found."
        )

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Capture dementia stage name before deletion
    dementia_stage_name = db_entry.Value

    # Soft delete the entry by setting IsDeleted to "1"
    db_entry.IsDeleted = "1"
    db_entry.ModifiedDate = datetime.now()
    db_entry.ModifiedById = modified_by

    # Commit the transaction to save the changes
    db.commit()
    db.refresh(db_entry)

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message=f"Deleted dementia stage: {dementia_stage_name}",
        table="PatientDementiaStageList",
        entity_id=stage_id,
        original_data=original_data_dict,
        updated_data=serialize_data(db_entry),
        log_type="system",
        is_system_config=True
    )
    return db_entry