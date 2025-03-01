# app/routers/allergy_reaction_type_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import allergy_reaction_type_crud as crud_reaction_type
from ..schemas.allergy_reaction_type import (
    AllergyReactionType,
    AllergyReactionTypeCreate,
    AllergyReactionTypeUpdate
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/get_allergy_reaction_types", response_model=list[AllergyReactionType], description="Get all allergy reaction types.")
def get_allergy_reaction_types(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation

    return crud_reaction_type.get_all_reaction_types(db)

@router.get("/get_allergy_reaction_type/{allergy_reaction_type_id}", response_model=AllergyReactionType, description="Get allergy reaction type by ID.")
def get_allergy_reaction_type(
    request: Request,
    allergy_reaction_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to False
):
    _ = extract_jwt_payload(request, require_auth)
    
    # No logging for this read operation
    db_reaction_type = crud_reaction_type.get_reaction_type_by_id(db, allergy_reaction_type_id)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type

@router.post("/create_allergy_reaction_types", response_model=AllergyReactionType)
def create_allergy_reaction_type(
    request: Request,
    reaction_type: AllergyReactionTypeCreate, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return crud_reaction_type.create_reaction_type(db, reaction_type, user_id, user_full_name)

@router.put("/update_allergy_reaction_type/{reaction_type_id}", response_model=AllergyReactionType)
def update_allergy_reaction_type(
    request: Request,
    allergy_reaction_type_id: int,
    reaction_type: AllergyReactionTypeUpdate, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_reaction_type = crud_reaction_type.update_reaction_type(db, allergy_reaction_type_id, reaction_type, user_id, user_full_name)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type

@router.delete("/delete_allergy_reaction_type/{reaction_type_id}", response_model=AllergyReactionType, description="Soft delete an allergy reaction type by marking it as active '0'")
def delete_allergy_reaction_type(
    request: Request,
    allergy_reaction_type_id: int, 
    db: Session = Depends(get_db),
    require_auth: bool = True  # Keep True for modifications
):  
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    db_reaction_type = crud_reaction_type.delete_reaction_type(db, allergy_reaction_type_id, user_id, user_full_name)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type 