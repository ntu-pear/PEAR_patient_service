from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_problem_list_model import PatientProblemList
from ..schemas.patient_problem_list import (
    PatientProblemListCreate,
    PatientProblemListUpdate,
)


def get_problem_lists(db: Session, pageNo: int = 0, pageSize: int = 100):
    """Get all problem list items with pagination"""
    query = db.query(PatientProblemList).filter(PatientProblemList.IsDeleted == '0')
    
    totalRecords = query.count()
    totalPages = (totalRecords + pageSize - 1) // pageSize if pageSize > 0 else 0
    
    offset = pageNo * pageSize
    db_problem_lists = query.order_by(PatientProblemList.ProblemName.asc()).offset(offset).limit(pageSize).all()
    
    return db_problem_lists, totalRecords, totalPages


def get_problem_list_by_id(db: Session, problem_list_id: int):
    """Get a specific problem list item by ID"""
    return db.query(PatientProblemList).filter(
        PatientProblemList.Id == problem_list_id,
        PatientProblemList.IsDeleted == '0'
    ).first()


def create_problem_list(
    db: Session, 
    problem_list: PatientProblemListCreate,
    created_by: str,
    user_full_name: str
):
    """Create a new problem list item with duplicate check and uppercase transformation"""
    # Convert ProblemName to UPPERCASE before checking and inserting
    uppercase_problem_name = problem_list.ProblemName.upper()
    
    # Check for existing problem list with same name (case-insensitive)
    existing_problem = db.query(PatientProblemList).filter(
        PatientProblemList.ProblemName == uppercase_problem_name,
        PatientProblemList.IsDeleted == '0'
    ).first()
    
    if existing_problem:
        raise HTTPException(
            status_code=400, 
            detail="A problem list entry with this name already exists"
        )
    
    try:
        data = problem_list.model_dump()
        data["ProblemName"] = uppercase_problem_name
        
        db_problem_list = PatientProblemList(
            **data,
            CreatedDate=datetime.now(),
            ModifiedDate=datetime.now(),
            CreatedByID=created_by,
            ModifiedByID=created_by,
            IsDeleted='0'
        )
        
        db.add(db_problem_list)
        db.commit()
        db.refresh(db_problem_list)

        updated_data_dict = serialize_data(data)
        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message=f"Created problem list item: {db_problem_list.ProblemName}",
            table="PatientProblemList",
            entity_id=db_problem_list.Id,
            original_data=None,
            updated_data=updated_data_dict,
            log_type = "system",
            is_system_config = True,
        )
        
        return db_problem_list
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def update_problem_list(
    db: Session,
    problem_list_id: int,
    problem_list: PatientProblemListUpdate,
    modified_by: str,
    user_full_name: str
):
    db_problem_list = db.query(PatientProblemList).filter(
        PatientProblemList.Id == problem_list_id,
        PatientProblemList.IsDeleted == '0'
    ).first()

    if not db_problem_list:
        return None

    update_data = problem_list.model_dump(exclude_unset=True)

    # Convert ProblemName to UPPERCASE if it's being updated
    if "ProblemName" in update_data and update_data["ProblemName"] is not None:
        update_data["ProblemName"] = update_data["ProblemName"].upper()

        # Only check for duplicates if the ProblemName is actually changing
        if update_data["ProblemName"] != db_problem_list.ProblemName:
            existing = db.query(PatientProblemList).filter(
                PatientProblemList.ProblemName == update_data["ProblemName"],
                PatientProblemList.IsDeleted == '0',
                PatientProblemList.Id != problem_list_id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="A problem list entry with this name already exists"
                )

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_problem_list.__dict__.items()
            if not k.startswith("_")
        }

        for key, value in update_data.items():
            setattr(db_problem_list, key, value)

        db_problem_list.ModifiedDate = datetime.now()
        db_problem_list.ModifiedByID = modified_by

        db.commit()
        db.refresh(db_problem_list)

        updated_data_dict = serialize_data(update_data)
        updated_data_dict["ProblemName"] = db_problem_list.ProblemName
        original_data_dict["ProblemName"] = db_problem_list.ProblemName

        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Updated problem list item: {db_problem_list.ProblemName}",
            table="PatientProblemList",
            entity_id=db_problem_list.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            log_type = "system",
            is_system_config = True,
        )

        return db_problem_list

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def delete_problem_list(
    db: Session, 
    problem_list_id: int,
    modified_by: str,
    user_full_name: str
):
    db_problem_list = db.query(PatientProblemList).filter(
        PatientProblemList.Id == problem_list_id,
        PatientProblemList.IsDeleted == '0'
    ).first()
    
    if not db_problem_list:
        return None

    try:
        original_data_dict = {
            k: serialize_data(v) for k, v in db_problem_list.__dict__.items() 
            if not k.startswith("_")
        }

        db_problem_list.IsDeleted = '1'
        db_problem_list.ModifiedDate = datetime.now()
        db_problem_list.ModifiedByID = modified_by
        
        db.commit()
        db.refresh(db_problem_list)

        original_data_dict["ProblemName"] = db_problem_list.ProblemName

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Deleted problem list item: {db_problem_list.ProblemName}",
            table="PatientProblemList",
            entity_id=problem_list_id,
            original_data=original_data_dict,
            updated_data={"IsDeleted": "1"},
            log_type = "system",
            is_system_config = True,
        )
        
        return db_problem_list
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))