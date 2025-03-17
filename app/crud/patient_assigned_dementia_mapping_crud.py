import math
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from ..models.patient_assigned_dementia_mapping_model import (
    PatientAssignedDementiaMapping,
)
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementia,
    PatientAssignedDementiaCreateResp,
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaUpdate,
)
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

# Get all dementia assignments with pagination
def get_all_assigned_dementias(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(
        PatientAssignedDementiaMapping.id,
        PatientAssignedDementiaMapping.PatientId,
        PatientAssignedDementiaMapping.DementiaTypeListId,
        PatientAssignedDementiaMapping.IsDeleted,
        PatientAssignedDementiaMapping.CreatedDate,
        PatientAssignedDementiaMapping.ModifiedDate,
        PatientAssignedDementiaMapping.CreatedById,
        PatientAssignedDementiaMapping.ModifiedById,
        PatientAssignedDementiaList.Value.label("DementiaTypeValue"),
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.IsDeleted == "0"
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    results = query.order_by(PatientAssignedDementiaMapping.id).offset(offset).limit(pageSize).all()

    assignments = [
        {
            "id": r.id,
            "PatientId": r.PatientId,
            "DementiaTypeListId": r.DementiaTypeListId,
            "IsDeleted": r.IsDeleted,
            "CreatedDate": r.CreatedDate,
            "ModifiedDate": r.ModifiedDate,
            "CreatedById": r.CreatedById,
            "ModifiedById": r.ModifiedById,
            "DementiaTypeValue": r.DementiaTypeValue,
        }
        for r in results
    ]

    return assignments, totalRecords, totalPages


# Get all dementia assignments for a patient with pagination
def get_assigned_dementias(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(
        PatientAssignedDementiaMapping.id,
        PatientAssignedDementiaMapping.PatientId,
        PatientAssignedDementiaMapping.DementiaTypeListId,
        PatientAssignedDementiaMapping.IsDeleted,
        PatientAssignedDementiaMapping.CreatedDate,
        PatientAssignedDementiaMapping.ModifiedDate,
        PatientAssignedDementiaMapping.CreatedById,
        PatientAssignedDementiaMapping.ModifiedById,
        PatientAssignedDementiaList.Value.label("DementiaTypeValue"),
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.PatientId == patient_id,
        PatientAssignedDementiaMapping.IsDeleted == "0"
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    results = query.order_by(PatientAssignedDementiaMapping.id).offset(offset).limit(pageSize).all()

    # ✅ Convert dictionary results into Pydantic model instances
    assignments = [
        PatientAssignedDementia(
            id=r.id,
            PatientId=r.PatientId,
            DementiaTypeListId=r.DementiaTypeListId,
            IsDeleted=r.IsDeleted,
            CreatedDate=r.CreatedDate,
            ModifiedDate=r.ModifiedDate,
            CreatedById=r.CreatedById,
            ModifiedById=r.ModifiedById,
            DementiaTypeValue=r.DementiaTypeValue
        ) for r in results
    ]

    return assignments, totalRecords, totalPages
def get_assigned_dementia_by_dementia_id(db: Session, dementia_id: int):
    result = db.query(
        PatientAssignedDementiaMapping,
        PatientAssignedDementiaList.Value.label("DementiaTypeValue")  # Include DementiaTypeValue
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.DementiaTypeListId == dementia_id,
        PatientAssignedDementiaMapping.IsDeleted == "0"
    ).first()

    if not result:
        return None

    # Convert the result into a dictionary including DementiaTypeValue
    assigned_dementia, dementia_type_value = result
    return {
        "id": assigned_dementia.id,
        "PatientId": assigned_dementia.PatientId,
        "DementiaTypeListId": assigned_dementia.DementiaTypeListId,
        "IsDeleted": assigned_dementia.IsDeleted,
        "CreatedDate": assigned_dementia.CreatedDate,
        "ModifiedDate": assigned_dementia.ModifiedDate,
        "CreatedById": assigned_dementia.CreatedById,
        "ModifiedById": assigned_dementia.ModifiedById,
        "DementiaTypeValue": dementia_type_value  # Ensure field is present
    }

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
    updated_data_dict = serialize_data({k: v for k, v in vars(new_assignment).items() if not k.startswith("_")})
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message="Created patient assigned dementia mapping",
        table="PatientAssignedDementiaMapping",
        entity_id=None,
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

    # Validate that the new DementiaTypeListId exists in PATIENT_ASSIGNED_DEMENTIA_LIST
    if dementia_data.DementiaTypeListId is not None:
        dementia_type_exists = (
            db.query(PatientAssignedDementiaList)
            .filter(
                PatientAssignedDementiaList.DementiaTypeListId == dementia_data.DementiaTypeListId,
                PatientAssignedDementiaList.IsDeleted == "0",
            )
            .first()
        )
        if not dementia_type_exists:
            raise HTTPException(
                status_code=400,
                detail=f"DementiaTypeListId {dementia_data.DementiaTypeListId} does not exist or has been deleted."
            )

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
        table="Patient Assigned Dementia Mapping",
        entity_id=dementia_id,
        original_data=original_data_dict,
        updated_data=None,
    )
    return db_assignment
