# app/routers/patient_highlight_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud.patient_highlight_crud import (
    get_all_highlights,
    get_highlights_by_patient,
    create_highlight,
    update_highlight,
    delete_highlight,
)
from ..schemas.patient_highlight import (
    PatientHighlight,
    PatientHighlightCreate,
    PatientHighlightUpdate,
)
from ..auth.jwt_utils import extract_jwt_payload, get_user_id, get_full_name
from ..logger.logger_utils import logger

router = APIRouter()

@router.get("/get_all_highlights", response_model=list[PatientHighlight], description="Get all highlights.")
def get_all_patient_highlights(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    return get_all_highlights(db)

@router.get("/get_highlights_by_patient/{patient_id}", response_model=list[PatientHighlight], description="Get highlights by patient ID.")
def get_patient_highlights(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    highlights = get_highlights_by_patient(db, patient_id)
    if not highlights:
        raise HTTPException(status_code=404, detail="No highlights found for the patient")
    return highlights

@router.post("/create_highlight", response_model=PatientHighlight, description="Create a new highlight.")
def create_patient_highlight(
    request: Request,
    highlight_data: PatientHighlightCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    logger.info(
        "Creating new patient highlight",
        extra={
            "user": user_id,
            "table": "PatientHighlight",
            "action": "create",
            "user_full_name": user_full_name
        }
    )
    return create_highlight(db, highlight_data, user_id)

@router.put("/update_highlight/{highlight_id}", response_model=PatientHighlight, description="Update an existing highlight.")
def update_patient_highlight(
    request: Request,
    highlight_id: int,
    highlight_data: PatientHighlightUpdate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    logger.info(
        "Updating patient highlight",
        extra={
            "user": user_id,
            "table": "PatientHighlight",
            "action": "update",
            "user_full_name": user_full_name,
            "entity_id": highlight_id
        }
    )
    return update_highlight(db, highlight_id, highlight_data, user_id)

@router.delete("/delete_highlight/{highlight_id}", response_model=PatientHighlight, description="Soft delete a highlight by ID.")
def delete_patient_highlight(
    request: Request,
    highlight_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    logger.info(
        "Deleting patient highlight",
        extra={
            "user": user_id,
            "table": "PatientHighlight",
            "action": "delete",
            "user_full_name": user_full_name,
            "entity_id": highlight_id
        }
    )
    return delete_highlight(db, highlight_id, user_id)