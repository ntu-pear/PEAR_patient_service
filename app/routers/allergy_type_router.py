# app/routers/allergy_type_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import allergy_type_crud as crud_allergy_type
from ..schemas.allergy_type import (
    AllergyType,
    AllergyTypeCreate,
    AllergyTypeUpdate
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/get_allergy_types", response_model=list[AllergyType], description="Get all allergy types.")
def get_allergy_types(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    return crud_allergy_type.get_all_allergy_types(db)

@router.get("/get_allergy_type/{allergy_type_id}", response_model=AllergyType, description="Get allergy type by ID.")
def get_allergy_type(
    request: Request,
    allergy_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    db_allergy_type = crud_allergy_type.get_allergy_type_by_id(db, allergy_type_id)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type

@router.post("/create_allergy_type", response_model=AllergyType, description="Create a new allergy type.")
def create_allergy_type(
    request: Request,
    allergy_type: AllergyTypeCreate, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"

    return crud_allergy_type.create_allergy_type(db, allergy_type, user_id, user_full_name)

@router.put("/update_allergy_type/{allergy_type_id}", response_model=AllergyType, description="Update an allergy type.")
def update_allergy_type(
    request: Request,
    allergy_type_id: int,
    allergy_type: AllergyTypeUpdate, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_allergy_type = crud_allergy_type.update_allergy_type(db, allergy_type_id, allergy_type, user_id, user_full_name)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type

@router.delete("/delete_allergy_type/{allergy_type_id}", response_model=AllergyType, description="Soft delete an allergy type by marking it as active '0'.")
def delete_allergy_type(
    request: Request,
    allergy_type_id: int, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_allergy_type = crud_allergy_type.delete_allergy_type(db, allergy_type_id, user_id, user_full_name)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type