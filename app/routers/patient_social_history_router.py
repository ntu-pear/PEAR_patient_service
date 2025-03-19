from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.crud.patient_privacy_level_crud import get_privacy_level_by_patient
from app.crud.social_history_sensitive_mapping_crud import get_all_sensitive_social_history
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
from httpx import AsyncClient


router = APIRouter()

@router.get("/SocialHistory", response_model=PatientSocialHistoryDecode, description="Get social history records by Patient ID.")
async def get_social_history(patient_id: int, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    #testing on ntu
    url = "http://192.168.188.171:5678"
    #testing on local
    #url = "http://127.0.0.1:8000"
    payload = extract_jwt_payload(request, require_auth)
    role_name = get_role_name(payload)
    
    async with AsyncClient() as client:
        response = await client.get(f"{url}/api/v1/roles/{role_name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error calling external API")
    
    db_user_privacy_level = response.json()
    db_patient_privacy_level = get_privacy_level_by_patient(db, patient_id)
    patient_social_history = crud_social_history.get_patient_social_history(db, patient_id)
    
    patient_privacy_level = db_patient_privacy_level.privacyLevelSensitive
    user_privacy_level = db_user_privacy_level.get("privacyLevelSensitive")

    if user_privacy_level >= patient_privacy_level.value:
        return patient_social_history

    sensitive_fields = {item.socialHistoryItem for item in get_all_sensitive_social_history(db)}
    
    masked_history = {}
    for key, value in patient_social_history.items():
        if key in sensitive_fields:
            masked_history[key] = -1  
        else:
            masked_history[key] = value

    return masked_history

@router.post("/SocialHistory/add", response_model=PatientSocialHistoryCreate)
def create_social_history(social_history: PatientSocialHistoryCreate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return crud_social_history.create_patient_social_history(db, social_history, user_id, user_full_name)

@router.put("/SocialHistory/update", response_model=PatientSocialHistoryUpdate)
def update_social_history(social_history: PatientSocialHistoryUpdate, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_social_history = crud_social_history.update_patient_social_history(db, social_history, user_id, user_full_name)
    if not db_social_history:
        raise HTTPException(status_code=404, detail="Social history not found")
    
    return db_social_history

@router.put("/SocialHistory/delete", response_model=PatientSocialHistory)
def delete_social_history(patient_id: int, social_history: PatientSocialHistoryDecode, request: Request, require_auth: bool = True, db: Session = Depends(get_db)):
    """
    Perform a soft delete on the social history record by changing 'isDeleted' from '0' to '1'.
    """
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == crud_patient_allocation.get_guardian_id_by_patient(db, social_history.patientId)
    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return crud_social_history.delete_patient_social_history(db, patient_id, user_id, user_full_name)
    
