from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import math
import logging

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_problem_model import PatientProblem
from ..models.patient_problem_list_model import PatientProblemList
from ..schemas.patient_problem import (
    PatientProblemCreate,
    PatientProblemUpdate,
)
from ..services.highlight_helper import create_highlight_if_needed

logger = logging.getLogger(__name__)


def get_problems(db: Session, pageNo: int = 0, pageSize: int = 10):
    """
    Get all patient problems with pagination.
    Uses joinedload to efficiently load problem_list relationship (ProblemName).
    """
    offset = pageNo * pageSize
    
    # Base query with joinedload for problem_list relationship
    query = db.query(PatientProblem).options(
        joinedload(PatientProblem.problem_list)
    ).filter(PatientProblem.IsDeleted == '0')
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0

    db_problems = (
        query.order_by(PatientProblem.Id.desc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    
    return db_problems, totalRecords, totalPages


def get_patient_problems(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 100):
    """
    Get all problems for a specific patient.
    Uses joinedload to efficiently load problem_list relationship (ProblemName).
    """
    offset = pageNo * pageSize
    
    # Base query with joinedload for problem_list relationship
    query = db.query(PatientProblem).options(
        joinedload(PatientProblem.problem_list)
    ).filter(
        PatientProblem.PatientID == patient_id,
        PatientProblem.IsDeleted == '0'
    )
    
    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize) if pageSize > 0 else 0

    db_problems = (
        query.order_by(PatientProblem.Id.desc())
        .offset(offset)
        .limit(pageSize)
        .all()
    )
    
    return db_problems, totalRecords, totalPages


def get_problem(db: Session, problem_id: int):
    """
    Get a specific problem by ID.
    Uses joinedload to efficiently load problem_list relationship (ProblemName).
    """
    return db.query(PatientProblem).options(
        joinedload(PatientProblem.problem_list)
    ).filter(
        PatientProblem.Id == problem_id,
        PatientProblem.IsDeleted == '0'
    ).first()


def create_problem(
    db: Session,
    problem_data: PatientProblemCreate,
    created_by: str,
    user_full_name: str
):
    """Create a new patient problem with highlight integration"""
    try:
        # Verify problem list exists
        problem_list = db.query(PatientProblemList).filter(
            PatientProblemList.Id == problem_data.ProblemListID,
            PatientProblemList.IsDeleted == '0'
        ).first()
        
        if not problem_list:
            raise HTTPException(
                status_code=404,
                detail=f"Problem list with ID {problem_data.ProblemListID} not found"
            )

        # Create problem record
        new_problem = PatientProblem(
            **problem_data.model_dump(),
            CreatedDate=datetime.now(),
            ModifiedDate=datetime.now(),
            CreatedByID=created_by,
            ModifiedByID=created_by,
            IsDeleted='0'
        )

        db.add(new_problem)
        db.flush()  # Get ID before commit

        # Generate highlight if needed
        create_highlight_if_needed(
            db=db,
            source_record=new_problem,
            type_code="PROBLEM",
            patient_id=new_problem.PatientID,
            source_table="PATIENT_PROBLEM",
            source_record_id=new_problem.Id,
            created_by=created_by
        )

        # Log action
        updated_data_dict = serialize_data(problem_data.model_dump())
        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created patient problem record",
            table="PatientProblem",
            entity_id=new_problem.Id,
            original_data=None,
            updated_data=updated_data_dict,
        )

        db.commit()
        
        # Reload with problem_list relationship for response
        db_problem_with_list = db.query(PatientProblem).options(
            joinedload(PatientProblem.problem_list)
        ).filter(
            PatientProblem.Id == new_problem.Id
        ).first()
        
        logger.info(f"Created problem {new_problem.Id} for patient {new_problem.PatientID}")
        return db_problem_with_list

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create problem: {str(e)}")


def update_problem(
    db: Session,
    problem_id: int,
    problem_data: PatientProblemUpdate,
    modified_by: str,
    user_full_name: str
):
    """Update a patient problem with highlight integration"""
    db_problem = db.query(PatientProblem).filter(
        PatientProblem.Id == problem_id,
        PatientProblem.IsDeleted == '0'
    ).first()

    if not db_problem:
        return None

    try:
        # Verify problem list if being updated
        update_data = problem_data.model_dump(exclude_unset=True)
        if 'ProblemListID' in update_data:
            problem_list = db.query(PatientProblemList).filter(
                PatientProblemList.Id == update_data['ProblemListID'],
                PatientProblemList.IsDeleted == '0'
            ).first()
            
            if not problem_list:
                raise HTTPException(
                    status_code=404,
                    detail=f"Problem list with ID {update_data['ProblemListID']} not found"
                )

        # Capture original data
        original_data_dict = {
            k: serialize_data(v) for k, v in db_problem.__dict__.items() 
            if not k.startswith("_")
        }

        # Update fields
        for key, value in update_data.items():
            setattr(db_problem, key, value)
        
        db_problem.ModifiedDate = datetime.now()
        db_problem.ModifiedByID = modified_by
        
        db.flush()

        # Update or remove highlight based on new data
        create_highlight_if_needed(
            db=db,
            source_record=db_problem,
            type_code="PROBLEM",
            patient_id=db_problem.PatientID,
            source_table="PATIENT_PROBLEM",
            source_record_id=db_problem.Id,
            created_by=modified_by
        )

        # Log action
        updated_data_dict = serialize_data(update_data)
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated patient problem record",
            table="PatientProblem",
            entity_id=db_problem.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )

        db.commit()
        
        # Reload with problem_list relationship for response
        db_problem_with_list = db.query(PatientProblem).options(
            joinedload(PatientProblem.problem_list)
        ).filter(
            PatientProblem.Id == db_problem.Id
        ).first()
        
        logger.info(f"Updated problem {db_problem.Id} for patient {db_problem.PatientID}")
        return db_problem_with_list

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update problem: {str(e)}")


def delete_problem(
    db: Session,
    problem_id: int,
    modified_by: str,
    user_full_name: str
):
    """Soft delete a patient problem and remove associated highlight"""
    db_problem = db.query(PatientProblem).filter(
        PatientProblem.Id == problem_id,
        PatientProblem.IsDeleted == '0'
    ).first()
    
    if not db_problem:
        return None

    try:
        # Capture original data
        original_data_dict = {
            k: serialize_data(v) for k, v in db_problem.__dict__.items() 
            if not k.startswith("_")
        }

        # Soft delete
        db_problem.IsDeleted = '1'
        db_problem.ModifiedDate = datetime.now()
        db_problem.ModifiedByID = modified_by
        
        db.flush()

        # Remove highlight (highlight_helper handles deletion)
        create_highlight_if_needed(
            db=db,
            source_record=db_problem,
            type_code="PROBLEM",
            patient_id=db_problem.PatientID,
            source_table="PATIENT_PROBLEM",
            source_record_id=db_problem.Id,
            created_by=modified_by
        )

        # Log action
        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Soft deleted patient problem record",
            table="PatientProblem",
            entity_id=problem_id,
            original_data=original_data_dict,
            updated_data={"IsDeleted": "1"}
        )

        db.commit()
        
        # Reload with problem_list relationship for response
        db_problem_with_list = db.query(PatientProblem).options(
            joinedload(PatientProblem.problem_list)
        ).filter(
            PatientProblem.Id == db_problem.Id
        ).first()
        
        logger.info(f"Deleted problem {db_problem.Id} for patient {db_problem.PatientID}")
        return db_problem_with_list

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete problem: {str(e)}")