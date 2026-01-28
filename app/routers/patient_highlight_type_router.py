# app/routers/patient_highlight_type_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud import patient_highlight_type_crud as crud_highlight_type
from ..database import get_db
from ..logger.logger_utils import logger
from ..schemas.patient_highlight_type import (
    HighlightType,
    HighlightTypeCreate,
    HighlightTypeUpdate,
)

router = APIRouter()

@router.get("/HighlightType/get_highlight_types", response_model=list[HighlightType], description="Get all highlight types.")
def get_highlight_types(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    return crud_highlight_type.get_all_highlight_types(db)

@router.get("/HighlightType/get_enabled_highlight_types", response_model=list[HighlightType], description="Get all enabled highlight types (IsEnabled = 1).")
def get_enabled_highlight_types(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    """
    Get all highlight types that are enabled (IsEnabled = 1/True).
    This filters out disabled types that admins have turned off.
    """
    _ = extract_jwt_payload(request, require_auth)
    return crud_highlight_type.get_enabled_highlight_types(db)

@router.patch("/toggle_highlight_type_enabled/{highlight_type_id}", response_model=HighlightType, description="Toggle the IsEnabled status of a highlight type.")
def toggle_highlight_type_enabled(
    request: Request,
    highlight_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return crud_highlight_type.toggle_highlight_type_enabled(db, highlight_type_id, user_id, user_full_name)


@router.get("/HighlightType/get_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Get highlight type by ID.")
def get_highlight_type(
    request: Request,
    highlight_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    db_highlight_type = crud_highlight_type.get_highlight_type_by_id(db, highlight_type_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type

@router.post("/HighlightType/create_highlight_type", response_model=HighlightType)
def create_highlight_type(
    request: Request,
    highlight_type: HighlightTypeCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return crud_highlight_type.create_highlight_type(db, highlight_type, user_id, user_full_name)

@router.put("/HighlightType/update_highlight_type/{highlight_type_id}", response_model=HighlightType)
def update_highlight_type(
    request: Request,
    highlight_type_id: int,
    highlight_type: HighlightTypeUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_highlight_type = crud_highlight_type.update_highlight_type(db, highlight_type_id, highlight_type, user_id, user_full_name)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type

@router.delete("/HighlightType/delete_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Soft delete a highlight type by marking it as IsDeleted '1'")
def delete_highlight_type(
    request: Request,
    highlight_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):  
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    db_highlight_type = crud_highlight_type.delete_highlight_type(db, highlight_type_id, user_id, user_full_name)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type