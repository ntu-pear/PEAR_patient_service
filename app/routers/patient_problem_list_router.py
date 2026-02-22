from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_problem_list_crud as crud_problem_list
from ..database import get_db
from ..schemas.patient_problem_list import (
    PatientProblemList,
    PatientProblemListCreate,
    PatientProblemListUpdate,
)
from ..schemas.response import PaginatedResponse, SingleResponse

router = APIRouter()


@router.get("/ProblemList", response_model=PaginatedResponse[PatientProblemList])
def get_problem_lists(
    request: Request,
    pageNo: int = 0,
    pageSize: int = 100,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    
    db_problem_lists, totalRecords, totalPages = crud_problem_list.get_problem_lists(
        db, 
        pageNo=pageNo, 
        pageSize=pageSize
    )
    
    problem_lists = [PatientProblemList.model_validate(p) for p in db_problem_lists]
    
    return PaginatedResponse(
        data=problem_lists,
        pageNo=pageNo,
        pageSize=pageSize,
        totalRecords=totalRecords,
        totalPages=totalPages
    )

@router.get("/ProblemList/{problem_list_id}", response_model=SingleResponse[PatientProblemList])
def get_problem_list(
    request: Request,
    problem_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    
    db_problem_list = crud_problem_list.get_problem_list_by_id(db, problem_list_id)
    
    if not db_problem_list:
        raise HTTPException(status_code=404, detail="Problem list item not found")

    problem_list = PatientProblemList.model_validate(db_problem_list)
    return SingleResponse(data=problem_list)


@router.post("/ProblemList/add", response_model=SingleResponse[PatientProblemList])
def create_problem_list(
    request: Request,
    problem_list: PatientProblemListCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem_list = crud_problem_list.create_problem_list(
        db, 
        problem_list, 
        user_id, 
        user_full_name
    )
    
    problem_list_response = PatientProblemList.model_validate(db_problem_list)
    return SingleResponse(data=problem_list_response)


@router.put("/ProblemList/update/{problem_list_id}", response_model=SingleResponse[PatientProblemList])
def update_problem_list(
    request: Request,
    problem_list_id: int,
    problem_list: PatientProblemListUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem_list = crud_problem_list.update_problem_list(
        db, 
        problem_list_id, 
        problem_list, 
        user_id, 
        user_full_name
    )
    
    if not db_problem_list:
        raise HTTPException(status_code=404, detail="Problem list item not found")

    problem_list_response = PatientProblemList.model_validate(db_problem_list)
    return SingleResponse(data=problem_list_response)


@router.delete("/ProblemList/delete/{problem_list_id}", response_model=SingleResponse[PatientProblemList])
def delete_problem_list(
    request: Request,
    problem_list_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    db_problem_list = crud_problem_list.delete_problem_list(
        db, 
        problem_list_id, 
        user_id, 
        user_full_name
    )
    
    if not db_problem_list:
        raise HTTPException(status_code=404, detail="Problem list item not found")

    problem_list_response = PatientProblemList.model_validate(db_problem_list)
    return SingleResponse(data=problem_list_response)