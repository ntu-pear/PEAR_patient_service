from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..models.social_history_sensitive_mapping_model import SocialHistorySensitiveMapping
from ..crud.social_history_sensitive_mapping_crud import create_sensitive_mapping, update_all_sensitive_mapping, delete_sensitive_mapping, get_all_social_history, get_all_sensitive_social_history, get_all_non_sensitive_social_history
from ..schemas.social_history_sensitive_mapping import SocialHistorySensitiveCreate, SocialHistorySensitiveUpdate, SocialHistorySensitive
from ..database import get_db
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_role_name

router = APIRouter()

@router.get("/social_history_sensitive_mapping", response_model=list[SocialHistorySensitive])
def read_all_social_history_sensitive_mapping(db: Session = Depends(get_db)):
    db_social_history_sensitive_mapping = get_all_social_history(db)
    if db_social_history_sensitive_mapping is None:
        raise HTTPException(status_code=404, detail="Social History Mapping not found")
    return db_social_history_sensitive_mapping

@router.post("/social_history_sensitive_mapping/add", response_model=SocialHistorySensitive)
def create_new_social_history_sensitive_mapping(request: Request, social_history_sensitive_mapping: SocialHistorySensitiveCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    role_name = get_role_name(payload)
    
    is_admin = role_name == "ADMIN"
    if not is_admin:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    return create_sensitive_mapping(db=db, social_history=social_history_sensitive_mapping, created_by=1)

@router.put("/social_history_sensitive_mapping/update", response_model=List[SocialHistorySensitive])
def update_all_social_history_sensitive_mapping(request: Request, social_history_sensitive_mapping_list: List[SocialHistorySensitiveUpdate], db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    role_name = get_role_name(payload)
    
    is_admin = role_name == "ADMIN"
    if not is_admin:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_social_history_sensitive_mapping = update_all_sensitive_mapping(db=db, social_history_list=social_history_sensitive_mapping_list, modified_by=1)
    if db_social_history_sensitive_mapping == []:
        raise HTTPException(status_code=404, detail="Social History Mapping not found")
    
    return db_social_history_sensitive_mapping

@router.delete("/social_history_sensitive_mapping/delete/{social_history_item}", response_model=SocialHistorySensitive)
def delete_existing_social_history_sensitive_mapping(request: Request, social_history_item: str, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    role_name = get_role_name(payload)
    
    is_admin = role_name == "ADMIN"
    if not is_admin:
        raise HTTPException(status_code=404, detail="User is not authorised")
    
    db_social_history_sensitive_mapping = delete_sensitive_mapping(db=db, social_history_item=social_history_item)
    if db_social_history_sensitive_mapping is None:
        raise HTTPException(status_code=404, detail="Social History Mapping not found")
    return db_social_history_sensitive_mapping