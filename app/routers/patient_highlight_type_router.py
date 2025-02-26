# app/routers/patient_highlight_type_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_highlight_type_crud as crud_highlight_type
from ..schemas.patient_highlight_type import HighlightType, HighlightTypeCreate, HighlightTypeUpdate
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/get_highlight_types", response_model=list[HighlightType], description="Get all highlight types.")
def get_highlight_types(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    return crud_highlight_type.get_all_highlight_types(db)

@router.get("/get_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Get highlight type by ID.")
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

@router.post("/create_highlight_type", response_model=HighlightType)
def create_highlight_type(
    request: Request,
    highlight_type: HighlightTypeCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
): 
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    logger.info(
        "Creating new highlight type",
        extra={
            "user": user_id,
            "table": "PatientHighlightType",
            "action": "create",
            "user_full_name": user_full_name
        }
    )
    return crud_highlight_type.create_highlight_type(db, highlight_type, user_id)

@router.put("/update_highlight_type/{highlight_type_id}", response_model=HighlightType)
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
    logger.info(
        "Updating highlight type",
        extra={
            "user": user_id,
            "table": "PatientHighlightType",
            "action": "update",
            "user_full_name": user_full_name,
            "entity_id": highlight_type_id
        }
    )
    db_highlight_type = crud_highlight_type.update_highlight_type(db, highlight_type_id, highlight_type, user_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type

@router.delete("/delete_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Soft delete a highlight type by marking it as IsDeleted '1'")
def delete_highlight_type(
    request: Request,
    highlight_type_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):  
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    logger.info(
        "Deleting highlight type",
        extra={
            "user": user_id,
            "table": "PatientHighlightType",
            "action": "delete",
            "user_full_name": user_full_name,
            "entity_id": highlight_type_id
        }
    )
    db_highlight_type = crud_highlight_type.delete_highlight_type(db, highlight_type_id, user_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type