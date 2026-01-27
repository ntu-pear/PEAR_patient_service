from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_problem_crud as crud_problem
from ..database import get_db
from ..schemas.patient_problem import (
    PatientProblem,
    PatientProblemCreate,
    PatientProblemUpdate,
    PatientProblemWithDetails,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()


@router.get("/Problems", response_model=PaginatedResponse[PatientProblemWithDetails])
def get_problems(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 10,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    
    db_problems, totalRecords, totalPages = crud_problem.get_problems(
        db, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    # Convert to response schema with ProblemName from loaded relationship
    problems_with_details = []
    for problem in db_problems:
        problem_dict = PatientProblem.model_validate(problem).model_dump()
        # Access loaded relationship directly (no additional query needed)
        problem_dict['ProblemName'] = problem.problem_list.ProblemName if problem.problem_list else None
        problems_with_details.append(PatientProblemWithDetails(**problem_dict))
    
    return PaginatedResponse(
        data=problems_with_details,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )


@router.get("/Patient/{patient_id}/Problems", response_model=PaginatedResponse[PatientProblemWithDetails])
def get_patient_problems(
    request: Request,
    patient_id: int,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    
    db_problems, totalRecords, totalPages = crud_problem.get_patient_problems(
        db,
        patient_id=patient_id,
        pageNo=pageNo,
        pageSize=pageSize
    )
    
    # Convert to response schema with ProblemName from loaded relationship
    problems_with_details = []
    for problem in db_problems:
        problem_dict = PatientProblem.model_validate(problem).model_dump()
        # Access loaded relationship directly (no additional query needed)
        problem_dict['ProblemName'] = problem.problem_list.ProblemName if problem.problem_list else None
        problems_with_details.append(PatientProblemWithDetails(**problem_dict))
    
    return PaginatedResponse(
        data=problems_with_details,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )


@router.get("/Problems/{problem_id}", response_model=SingleResponse[PatientProblemWithDetails])
def get_problem(
    request: Request,
    problem_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    
    db_problem = crud_problem.get_problem(db, problem_id)
    
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Convert to response schema with ProblemName from loaded relationship
    problem_dict = PatientProblem.model_validate(db_problem).model_dump()
    # Access loaded relationship directly (no additional query needed)
    problem_dict['ProblemName'] = db_problem.problem_list.ProblemName if db_problem.problem_list else None
    problem_with_details = PatientProblemWithDetails(**problem_dict)
    
    return SingleResponse(data=problem_with_details)


@router.post("/Problems/add", response_model=SingleResponse[PatientProblemWithDetails])
def create_problem(
    request: Request,
    problem: PatientProblemCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem = crud_problem.create_problem(
        db,
        problem,
        user_id,
        user_full_name
    )
    
    # CRUD now returns problem with relationship already loaded via joinedload
    problem_dict = PatientProblem.model_validate(db_problem).model_dump()
    problem_dict['ProblemName'] = db_problem.problem_list.ProblemName if db_problem.problem_list else None
    problem_with_details = PatientProblemWithDetails(**problem_dict)
    
    return SingleResponse(data=problem_with_details)


@router.put("/Problems/update/{problem_id}", response_model=SingleResponse[PatientProblemWithDetails])
def update_problem(
    request: Request,
    problem_id: int,
    problem: PatientProblemUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem = crud_problem.update_problem(
        db,
        problem_id,
        problem,
        user_id,
        user_full_name
    )
    
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # CRUD now returns problem with relationship already loaded via joinedload
    problem_dict = PatientProblem.model_validate(db_problem).model_dump()
    problem_dict['ProblemName'] = db_problem.problem_list.ProblemName if db_problem.problem_list else None
    problem_with_details = PatientProblemWithDetails(**problem_dict)
    
    return SingleResponse(data=problem_with_details)


@router.delete("/Problems/delete/{problem_id}", response_model=SingleResponse[PatientProblemWithDetails])
def delete_problem(
    request: Request,
    problem_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem = crud_problem.delete_problem(
        db,
        problem_id,
        user_id,
        user_full_name
    )
    
    if not db_problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem_dict = PatientProblem.model_validate(db_problem).model_dump()
    problem_dict['ProblemName'] = db_problem.problem_list.ProblemName if db_problem.problem_list else None
    problem_with_details = PatientProblemWithDetails(**problem_dict)
    
    return SingleResponse(data=problem_with_details)