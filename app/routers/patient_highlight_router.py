# app/routers/patient_highlight_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth.jwt_utils import extract_jwt_payload, get_full_name, get_user_id
from ..crud.patient_highlight_crud import (
    create_highlight,
    delete_highlight,
    get_all_highlights,
    get_enabled_highlights,
    get_enabled_highlights_by_patient,
    get_highlights_by_patient,
    update_highlight,
)
from ..database import get_db
from ..logger.logger_utils import logger
from ..schemas.patient_highlight import (
    PatientHighlight,
    PatientHighlightCreate,
    PatientHighlightUpdate,
)

router = APIRouter()

@router.get("/Highlight/get_all_highlights", response_model=list[PatientHighlight], description="Get all highlights.")
def get_all_patient_highlights(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    _ = extract_jwt_payload(request, require_auth)
    # No logging for this read operation
    return get_all_highlights(db)

@router.get("/Highlight/get_highlights_by_patient/{patient_id}", response_model=list[PatientHighlight], description="Get highlights by patient ID.")
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

@router.get("/Highlight/get_enabled_highlights", response_model=list[PatientHighlight], description="Get all highlights where IsDeleted=0 and the type's IsEnabled=1.")
def get_all_enabled_highlights(
    request: Request,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    
    _ = extract_jwt_payload(request, require_auth)
    return get_enabled_highlights(db)

@router.get("/Highlight/get_enabled_highlights_by_patient/{patient_id}", response_model=list[PatientHighlight], description="Get enabled highlights for a specific patient.")
def get_patient_enabled_highlights(
    request: Request,
    patient_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    
    _ = extract_jwt_payload(request, require_auth)
    highlights = get_enabled_highlights_by_patient(db, patient_id)
    if not highlights:
        raise HTTPException(status_code=404, detail="No enabled highlights found for the patient")
    return highlights

@router.post("/Highlight/create_highlight", response_model=PatientHighlight, description="Create a new highlight.")
def create_patient_highlight(
    request: Request,
    highlight_data: PatientHighlightCreate,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    return create_highlight(db, highlight_data, user_id, user_full_name)

@router.put("/Highlight/update_highlight/{highlight_id}", response_model=PatientHighlight, description="Update an existing highlight.")
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
    
    return update_highlight(db, highlight_id, highlight_data, user_id, user_full_name)

@router.delete("/Highlight/delete_highlight/{highlight_id}", response_model=PatientHighlight, description="Soft delete a highlight by ID.")
def delete_patient_highlight(
    request: Request,
    highlight_id: int,
    db: Session = Depends(get_db),
    require_auth: bool = True  # Default to True
):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    user_full_name = get_full_name(payload) or "Anonymous User"
    
    return delete_highlight(db, highlight_id, user_id, user_full_name)