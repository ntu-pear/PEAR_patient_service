from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter()

@router.get("/get_all_highlights", response_model=list[PatientHighlight], description="Get all highlights.")
def get_all_patient_highlights(db: Session = Depends(get_db)):
    return get_all_highlights(db)

@router.get("/get_highlights_by_patient/{patient_id}", response_model=list[PatientHighlight], description="Get highlights by patient ID.")
def get_patient_highlights(patient_id: int, db: Session = Depends(get_db)):
    highlights = get_highlights_by_patient(db, patient_id)
    if not highlights:
        raise HTTPException(status_code=404, detail="No highlights found for the patient")
    return highlights

@router.post("/create_highlight", response_model=PatientHighlight, description="Create a new highlight.")
def create_patient_highlight(highlight_data: PatientHighlightCreate, db: Session = Depends(get_db)):
    # Replace with actual user ID in a real-world scenario
    created_by = 1
    return create_highlight(db, highlight_data, created_by)

@router.put("/update_highlight/{highlight_id}", response_model=PatientHighlight, description="Update an existing highlight.")
def update_patient_highlight(highlight_id: int, highlight_data: PatientHighlightUpdate, db: Session = Depends(get_db)):
    # Replace with actual user ID in a real-world scenario
    modified_by = 1
    return update_highlight(db, highlight_id, highlight_data, modified_by)

@router.delete("/delete_highlight/{highlight_id}", response_model=PatientHighlight, description="Soft delete a highlight by ID.")
def delete_patient_highlight(highlight_id: int, db: Session = Depends(get_db)):
    # Replace with actual user ID in a real-world scenario
    modified_by = 1
    return delete_highlight(db, highlight_id, modified_by)
