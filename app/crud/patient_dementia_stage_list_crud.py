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
        ).all()
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
    # Check if a stage with the same name already exists
    existing_stage = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.DementiaStage == stage_data.DementiaStage,
        PatientDementiaStageList.IsDeleted == "0"
    ).first()
    
    if existing_stage:
        raise HTTPException(
            status_code=400, 
            detail=f"Dementia stage '{stage_data.DementiaStage}' already exists."
        )
    
    new_entry = PatientDementiaStageList(
        DementiaStage=stage_data.DementiaStage,
        IsDeleted="0",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    
    updated_data_dict = serialize_data(stage_data.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created dementia stage list entry",
        table="PatientDementiaStageList",
        entity_id=new_entry.id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return new_entry

def update_dementia_stage_list_entry(
    db: Session, 
    stage_id: int, 
    stage_data: PatientDementiaStageListUpdate, 
    modified_by: str, 
    user_full_name: str
):
    # Query the database for the entry to update
    db_entry = db.query(PatientDementiaStageList).filter(
        PatientDementiaStageList.id == stage_id,
        PatientDementiaStageList.IsDeleted == '0',
    ).first()

    if not db_entry:
        return None

    # Check if updating to a stage name that already exists
    if stage_data.DementiaStage:
        existing_stage = db.query(PatientDementiaStageList).filter(
            PatientDementiaStageList.DementiaStage == stage_data.DementiaStage,
            PatientDementiaStageList.id != stage_id,
            PatientDementiaStageList.IsDeleted == "0"
        ).first()
        
        if existing_stage:
            raise HTTPException(
                status_code=400, 
                detail=f"Dementia stage '{stage_data.DementiaStage}' already exists."
            )

    # Update the fields of the entry
    update_data = stage_data.model_dump(exclude={"id"}, exclude_unset=True)

    try: 
        original_data_dict = {
            k: serialize_data(v) for k, v in db_entry.__dict__.items() if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    for key, value in update_data.items():
        setattr(db_entry, key, value)

    # Update the modified fields
    db_entry.ModifiedDate = datetime.now()
    db_entry.ModifiedById = modified_by

    try:
        db.commit()
        db.refresh(db_entry)

        updated_data_dict = serialize_data(stage_data.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated dementia stage list entry",
            table="PatientDementiaStageList",
            entity_id=stage_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
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
        message="Deleted dementia stage list entry",
        table="PatientDementiaStageList",
        entity_id=stage_id,
        original_data=original_data_dict,
        updated_data=serialize_data(db_entry),
    )
    return db_entry