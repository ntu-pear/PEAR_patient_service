import math
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_assigned_dementia_list_model import PatientAssignedDementiaList
from ..models.patient_assigned_dementia_mapping_model import (
    PatientAssignedDementiaMapping,
)
from ..models.patient_dementia_stage_list_model import PatientDementiaStageList
from ..schemas.patient_assigned_dementia_mapping import (
    PatientAssignedDementia,
    PatientAssignedDementiaCreate,
    PatientAssignedDementiaCreateResp,
    PatientAssignedDementiaUpdate,
)


# Get all dementia assignments with pagination
def get_all_assigned_dementias(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientAssignedDementiaMapping).options(
        joinedload(PatientAssignedDementiaMapping._dementia_stage)
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.IsDeleted == "0"
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    results = query.order_by(PatientAssignedDementiaMapping.id.desc()).offset(offset).limit(pageSize).all()

    assignments = []
    for r in results:
        dementia_type = db.query(PatientAssignedDementiaList.Value).filter(
            PatientAssignedDementiaList.DementiaTypeListId == r.DementiaTypeListId
        ).scalar()
        
        assignments.append({
            "id": r.id,
            "PatientId": r.PatientId,
            "DementiaTypeListId": r.DementiaTypeListId,
            "DementiaStageId": r.DementiaStageId,
            "IsDeleted": r.IsDeleted,
            "CreatedDate": r.CreatedDate,
            "ModifiedDate": r.ModifiedDate,
            "CreatedById": r.CreatedById,
            "ModifiedById": r.ModifiedById,
            "DementiaTypeValue": dementia_type,
            "dementia_stage_value": r.dementia_stage_value,
        })

    return assignments, totalRecords, totalPages

# Get all dementia assignments for a patient with pagination
def get_assigned_dementias(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(PatientAssignedDementiaMapping).options(
        joinedload(PatientAssignedDementiaMapping._dementia_stage)
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.PatientId == patient_id,
        PatientAssignedDementiaMapping.IsDeleted == "0"
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    results = query.order_by(PatientAssignedDementiaMapping.id.desc()).offset(offset).limit(pageSize).all()

    # Convert to Pydantic model instances
    assignments = []
    for r in results:
        dementia_type = db.query(PatientAssignedDementiaList.Value).filter(
            PatientAssignedDementiaList.DementiaTypeListId == r.DementiaTypeListId
        ).scalar()
        
        assignments.append(
            PatientAssignedDementia(
                id=r.id,
                PatientId=r.PatientId,
                DementiaTypeListId=r.DementiaTypeListId,
                DementiaStageId=r.DementiaStageId,
                IsDeleted=r.IsDeleted,
                CreatedDate=r.CreatedDate,
                ModifiedDate=r.ModifiedDate,
                CreatedById=r.CreatedById,
                ModifiedById=r.ModifiedById,
                DementiaTypeValue=dementia_type,
                dementia_stage_value=r.dementia_stage_value
            )
        )

    return assignments, totalRecords, totalPages
def get_assigned_dementia_by_dementia_id(db: Session, dementia_id: int):
    result = db.query(PatientAssignedDementiaMapping).options(
        joinedload(PatientAssignedDementiaMapping._dementia_stage)
    ).join(
        PatientAssignedDementiaList,
        PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId
    ).filter(
        PatientAssignedDementiaMapping.DementiaTypeListId == dementia_id,
        PatientAssignedDementiaMapping.IsDeleted == "0"
    ).first()

    if not result:
        return None
    
    # Get dementia type value
    dementia_type = db.query(PatientAssignedDementiaList.Value).filter(
        PatientAssignedDementiaList.DementiaTypeListId == result.DementiaTypeListId
    ).scalar()
    
    return {
        "id": result.id,
        "PatientId": result.PatientId,
        "DementiaTypeListId": result.DementiaTypeListId,
        "DementiaStageId": result.DementiaStageId,
        "IsDeleted": result.IsDeleted,
        "CreatedDate": result.CreatedDate,
        "ModifiedDate": result.ModifiedDate,
        "CreatedById": result.CreatedById,
        "ModifiedById": result.ModifiedById,
        "DementiaTypeValue": dementia_type,
        "dementia_stage_value": result.dementia_stage_value
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

    # Validate DementiaStageId if provided
    if dementia_data.DementiaStageId is not None:
        dementia_stage = (
            db.query(PatientDementiaStageList)
            .filter(
                PatientDementiaStageList.id == dementia_data.DementiaStageId,
                PatientDementiaStageList.IsDeleted == "0",
            )
            .first()
        )
        if not dementia_stage:
            raise HTTPException(status_code=400, detail="Invalid or deleted dementia stage")

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
        DementiaStageId=dementia_data.DementiaStageId,
        IsDeleted="0",
        CreatedDate=datetime.now(),
        ModifiedDate=datetime.now(),
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

    # Validate DementiaStageId if being updated
    if dementia_data.DementiaStageId is not None:
        dementia_stage_exists = (
            db.query(PatientDementiaStageList)
            .filter(
                PatientDementiaStageList.id == dementia_data.DementiaStageId,
                PatientDementiaStageList.IsDeleted == "0",
            )
            .first()
        )
        if not dementia_stage_exists:
            raise HTTPException(
                status_code=400,
                detail=f"DementiaStageId {dementia_data.DementiaStageId} does not exist or has been deleted."
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
    db_assignment.ModifiedDate = datetime.now()
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
    db_assignment.ModifiedDate = datetime.now()
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
