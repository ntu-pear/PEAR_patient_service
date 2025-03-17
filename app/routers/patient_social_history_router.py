from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_social_history_crud as crud_social_history
from ..crud import patient_allocation_crud as crud_patient_allocation
from ..schemas.patient_social_history import (
    PatientSocialHistory,
    PatientSocialHistoryCreate,
    PatientSocialHistoryUpdate,
    PatientSocialHistoryDecode
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name, get_role_name


router = APIRouter()

@router.get("/SocialHistory", response_model=PatientSocialHistoryDecode, description="Get social history records by Patient ID.")
def get_social_history(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    _ = extract_jwt_payload(request, require_auth)

    db_social_history = crud_social_history.get_patient_social_history(db, patient_id)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    return db_social_history

@router.post("/SocialHistory/add", response_model=PatientSocialHistoryCreate)
def create_social_history(social_history: PatientSocialHistoryCreate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor or not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return crud_social_history.create_patient_social_history(db, social_history, user_id, user_full_name)

@router.put("/SocialHistory/update", response_model=PatientSocialHistoryUpdate)
def update_social_history(patient_id: int, social_history: PatientSocialHistoryUpdate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor or not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_social_history = crud_social_history.update_patient_social_history(db, patient_id, social_history, user_id, user_full_name)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    
    return db_social_history

@router.put("/SocialHistory/delete", response_model=PatientSocialHistory)
def delete_social_history(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    """
    Perform a soft delete on the social history record by changing 'isDeleted' from '0' to '1'.
    """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor or not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return crud_social_history.delete_patient_social_history(db, patient_id, user_id, user_full_name)
    
