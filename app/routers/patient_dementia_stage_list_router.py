from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_dementia_stage_list_crud as crud_dementia_stage
from ..schemas.patient_dementia_stage_list import (
    PatientDementiaStageList,
    PatientDementiaStageListCreate,
    PatientDementiaStageListUpdate,
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name

router = APIRouter()

@router.get(
    "/DementiaStage/List", 
    response_model=list[PatientDementiaStageList],
    description="Retrieve all dementia stage list entries."
)
def get_all_dementia_stage_lists(
    request: Request, 
    db: Session = Depends(get_db), 
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    return crud_dementia_stage.get_all_dementia_stage_list_entries(db)


@router.get(
    "/DementiaStage/List/{dementia_stage_id}", 
    response_model=PatientDementiaStageList,
    description="Retrieve a single dementia stage list entry by ID."
)
def get_dementia_stage_list_by_id(
    request: Request, 
    stage_id: int, 
    db: Session = Depends(get_db), 
    require_auth: bool = True
):
    _ = extract_jwt_payload(request, require_auth)
    stage_entry = crud_dementia_stage.get_dementia_stage_list_entry_by_id(db, stage_id)
    if not stage_entry:
        raise HTTPException(status_code=404, detail="Dementia stage list entry not found")
    return stage_entry


@router.post(
    "/DementiaStage/List/add", 
    response_model=PatientDementiaStageList,
    description="Create a new dementia stage list entry."
)
def create_dementia_stage_list_entry(
    request: Request, 
    stage_data: PatientDementiaStageListCreate, 
    db: Session = Depends(get_db), 
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return crud_dementia_stage.create_dementia_stage_list_entry(
        db, stage_data, user_id, user_full_name
    )

@router.put(
    "/DementiaStage/List/update/{dementia_stage_id}", 
    response_model=PatientDementiaStageList,
    description="Update an existing dementia stage list entry."
)
def update_dementia_stage_list_entry(
    request: Request, 
    stage_id: int, 
    stage_data: PatientDementiaStageListUpdate, 
    db: Session = Depends(get_db), 
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    updated_entry = crud_dementia_stage.update_dementia_stage_list_entry(
        db, stage_id, stage_data, user_id, user_full_name
    )
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Dementia stage list entry not found")
    return updated_entry


@router.delete(
    "/DementiaStage/List/delete/{dementia_stage_id}", 
    response_model=PatientDementiaStageList,
    description="Soft delete a dementia stage list entry."
)
def delete_dementia_stage_list_entry(
    request: Request, 
    stage_id: int, 
    db: Session = Depends(get_db), 
    require_auth: bool = True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    deleted_entry = crud_dementia_stage.delete_dementia_stage_list_entry(
        db, stage_id, user_id, user_full_name
    )
    if not deleted_entry:
        raise HTTPException(status_code=404, detail="Dementia stage list entry not found")
    return deleted_entry