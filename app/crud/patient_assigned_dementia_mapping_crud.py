from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from ..models.patient_assigned_dementia_mapping_model import (
    PatientAssignedDementiaMapping,
)
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaUpdate,
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data


# Get all dementia assignments across all patients
def get_all_assigned_dementias(db: Session):
    results = (
        db.query(
            PatientAssignedDementiaMapping.id,
            PatientAssignedDementiaMapping.PatientId,
            PatientAssignedDementiaMapping.DementiaTypeListId,  # Include this field
            PatientAssignedDementiaMapping.IsDeleted,
            PatientAssignedDementiaMapping.CreatedDate,
            PatientAssignedDementiaMapping.ModifiedDate,
            PatientAssignedDementiaMapping.CreatedById,
            PatientAssignedDementiaMapping.ModifiedById,
            PatientAssignedDementiaList.Value.label("DementiaTypeValue"),
        )
        .join(
            PatientAssignedDementiaList,
            PatientAssignedDementiaMapping.DementiaTypeListId
            == PatientAssignedDementiaList.DementiaTypeListId,
        )
        .filter(
            PatientAssignedDementiaMapping.IsDeleted == "0"
        )  # Filter only not deleted
        .all()
    )

    dementia_assignments = []
    for result in results:
        dementia_assignments.append(
            {
                "id": result.id,
                "PatientId": result.PatientId,
                "DementiaTypeListId": result.DementiaTypeListId,  # Add this field
                "IsDeleted": result.IsDeleted,
                "CreatedDate": result.CreatedDate,
                "ModifiedDate": result.ModifiedDate,
                "CreatedById": result.CreatedById,
                "ModifiedById": result.ModifiedById,
                "DementiaTypeValue": result.DementiaTypeValue,
            }
        )

    return dementia_assignments


# Get all dementia assignments for a patient
def get_assigned_dementias(db: Session, patient_id: int):
    results = (
        db.query(
            PatientAssignedDementiaMapping.id,
            PatientAssignedDementiaMapping.PatientId,
            PatientAssignedDementiaMapping.DementiaTypeListId,  # Include this field
            PatientAssignedDementiaMapping.IsDeleted,
            PatientAssignedDementiaMapping.CreatedDate,
            PatientAssignedDementiaMapping.ModifiedDate,
            PatientAssignedDementiaMapping.CreatedById,
            PatientAssignedDementiaMapping.ModifiedById,
            PatientAssignedDementiaList.Value.label("DementiaTypeValue"),
        )
        .join(
            PatientAssignedDementiaList,
            PatientAssignedDementiaMapping.DementiaTypeListId
            == PatientAssignedDementiaList.DementiaTypeListId,
        )
        .filter(
            PatientAssignedDementiaMapping.PatientId == patient_id,
            PatientAssignedDementiaMapping.IsDeleted == "0",
        )
        .all()
    )

    dementia_assignments = []
    for result in results:
        dementia_assignments.append(
            {
                "id": result.id,
                "PatientId": result.PatientId,
                "DementiaTypeListId": result.DementiaTypeListId,  # Add this field
                "IsDeleted": result.IsDeleted,
                "CreatedDate": result.CreatedDate,
                "ModifiedDate": result.ModifiedDate,
                "CreatedById": result.CreatedById,
                "ModifiedById": result.ModifiedById,
                "DementiaTypeValue": result.DementiaTypeValue,
            }
        )

    return dementia_assignments


# Create a new dementia assignment
def create_assigned_dementia(
    db: Session, dementia_data: PatientAssignedDementiaCreate, created_by: str, user_full_name:str
):
    # Check if the dementia type exists and is not deleted
    dementia_type = (
        db.query(PatientAssignedDementiaList)
        .filter(
            PatientAssignedDementiaList.DementiaTypeListId
            == dementia_data.DementiaTypeListId,
            PatientAssignedDementiaList.IsDeleted == "0",
        )
        .first()
    )
    if not dementia_type:
        raise HTTPException(status_code=400, detail="Invalid or deleted dementia type")

    # Check if the patient already has this dementia type assigned
    existing_assignment = (
        db.query(PatientAssignedDementiaMapping)
        .filter(
            PatientAssignedDementiaMapping.PatientId == dementia_data.PatientId,
            PatientAssignedDementiaMapping.DementiaTypeListId
            == dementia_data.DementiaTypeListId,
            PatientAssignedDementiaMapping.IsDeleted == "0",
        )
        .first()
    )

    if existing_assignment:
        raise HTTPException(
            status_code=400, detail="Patient already assigned this dementia type"
        )

    # Create the new assignment
    new_assignment = PatientAssignedDementiaMapping(
        PatientId=dementia_data.PatientId,
        DementiaTypeListId=dementia_data.DementiaTypeListId,
        IsDeleted="0",
        CreatedDate=datetime.utcnow(),
        ModifiedDate=datetime.utcnow(),
        CreatedById=created_by,
        ModifiedById=created_by,
    )
    updated_data_dict = serialize_data(dementia_data.model_dump())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created patient assigned dementia mapping",
        table="PatientAssignedDementiaMapping",
        entity_id=new_assignment.id,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return new_assignment


# Update a dementia assignment
def update_assigned_dementia(
    db: Session,
    dementia_id: int,
    dementia_data: PatientAssignedDementiaUpdate,
    modified_by: str,
    user_full_name: str
):
    db_assignment = (
        db.query(PatientAssignedDementiaMapping)
        .filter(
            PatientAssignedDementiaMapping.id == dementia_id,
            PatientAssignedDementiaMapping.IsDeleted == "0",
        )
        .first()
    )

    if not db_assignment:
        raise HTTPException(status_code=404, detail="Dementia assignment not found")

    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_assignment.__dict__.items()
            if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Update the assignment
    for key, value in dementia_data.model_dump(exclude_unset=True).items():
        setattr(db_assignment, key, value)

    # Update metadata
    db_assignment.ModifiedDate = datetime.utcnow()
    db_assignment.ModifiedById = modified_by

    db.commit()
    db.refresh(db_assignment)

    updated_data_dict = serialize_data(dementia_data.model_dump())
    log_crud_action(
        action=ActionType.UPDATE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Updated patient assigned dementia mapping",
        table="PatientAssignedDementiaMapping",
        entity_id=dementia_id,
        original_data=original_data_dict,
        updated_data=updated_data_dict,
    )
    return db_assignment


# Soft delete a dementia assignment (set IsDeleted to '1')
def delete_assigned_dementia(db: Session, dementia_id: int, modified_by: str, user_full_name: str):
    db_assignment = (
        db.query(PatientAssignedDementiaMapping)
        .filter(
            PatientAssignedDementiaMapping.id == dementia_id,
            PatientAssignedDementiaMapping.IsDeleted == "0",
        )
        .first()
    )

    if not db_assignment:
        raise HTTPException(status_code=404, detail="Dementia assignment not found")

    try:
        original_data_dict = {
            k: serialize_data(v)
            for k, v in db_assignment.__dict__.items()
            if not k.startswith("_")
        }
    except Exception as e:
        original_data_dict = "{}"

    # Soft delete the assignment
    db_assignment.IsDeleted = "1"
    db_assignment.ModifiedDate = datetime.utcnow()
    db_assignment.ModifiedById = modified_by

    db.commit()
    db.refresh(db_assignment)

    log_crud_action(
        action=ActionType.DELETE,
        user=modified_by,
        user_full_name=user_full_name,
        message="Deleted patient assigned dementia mapping",
        table="PatientAssignedDementiaMapping",
        entity_id=dementia_id,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_assignment
