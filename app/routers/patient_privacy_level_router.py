from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from httpx import AsyncClient
from ..schemas.patient_privacy_level import PatientPrivacyLevelCreate, PatientPrivacyLevelUpdate, PatientPrivacyLevel
from ..schemas.patient_social_history import PatientSocialHistoryBase
from ..crud.patient_privacy_level_crud import get_privacy_level_by_patient, get_privacy_levels_by_patient, create_patient_privacy_level, update_patient_privacy_level, delete_patient_privacy_level
from ..crud.patient_patient_guardian_crud import get_all_patient_guardian_by_patientId
from ..crud.patient_social_history_crud import get_patient_social_history
from ..crud.social_history_sensitive_mapping_crud import get_all_sensitive_social_history
from ..crud.patient_allocation_crud import get_guardian_id_by_patient
from ..database import get_db
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_role_name
from ..models.patient_privacy_level_model import PrivacyStatus

router = APIRouter()

@router.get("/privacy_level_patient/{patient_id}", response_model=PatientPrivacyLevel)
def read_privacy_level_by_patient(patient_id: int, db: Session = Depends(get_db)):
    db_privacy_setting = get_privacy_level_by_patient(db, patient_id=patient_id)
    if db_privacy_setting is None:
        raise HTTPException(status_code=404, detail="Privacy user setting not found")
    return db_privacy_setting

@router.get("/privacy_levels_patient/", response_model=list[PatientPrivacyLevel])
def read_privacy_levels(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    privacy_settings = get_privacy_levels_by_patient(db, skip=skip, limit=limit)
    return privacy_settings

@router.post("/privacy_levels/add", response_model=PatientPrivacyLevel)
def create_new_privacy_level_setting(request: Request, patient_id: str, privacy_level_setting: PatientPrivacyLevelCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload)
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == get_guardian_id_by_patient(db, patient_id)

    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return create_patient_privacy_level(db=db, patient_id=patient_id, patient_privacy_level=privacy_level_setting, created_by=1)

@router.put("/privacy_levels/update/{patient_id}", response_model=PatientPrivacyLevel)
def update_existing_privacy_level_setting(request: Request, patient_id: str, privacy_level_setting: PatientPrivacyLevelUpdate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload)
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == get_guardian_id_by_patient(db, patient_id)
    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_privacy_setting = update_patient_privacy_level(db=db, patient_id=patient_id, patient_privacy_level=privacy_level_setting, modified_by=1)
    if db_privacy_setting is None:
        raise HTTPException(status_code=404, detail="Privacy setting not found")
    
    return db_privacy_setting

@router.delete("/privacy_levels/delete/{patient_id}", response_model=PatientPrivacyLevel)
def delete_existing_privacy_level_setting(request: Request, patient_id: str, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload)
    role_name = get_role_name(payload)
    
    is_supervisor = role_name == "SUPERVISOR"
    valid_primary_guardian = role_name == "GUARDIAN" and user_id == get_guardian_id_by_patient(db, patient_id)
    if not is_supervisor and not valid_primary_guardian:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_privacy_setting = delete_patient_privacy_level(db=db, patient_id=patient_id)
    if db_privacy_setting is None:
        raise HTTPException(status_code=404, detail="Privacy setting not found")
    return db_privacy_setting

@router.get("/privacy_settings/evaluate", response_model=PatientSocialHistoryBase)
async def evaluate_privacy_level(request: Request, patient_id: str, db: Session = Depends(get_db), require_auth: bool = True):
    url = "http://127.0.0.1:8000"
    payload = extract_jwt_payload(request, require_auth)
    role_name = get_role_name(payload)
    
    async with AsyncClient() as client:
        response = await client.get(f"{url}/api/v1/roles/{role_name}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error calling external API")
    
    db_user_privacy_level = response.json()
    db_patient_privacy_level = get_privacy_level_by_patient(db, patient_id)
    patient_social_history = get_patient_social_history(db, patient_id)
    
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