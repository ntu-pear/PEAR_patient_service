from sqlalchemy.orm import Session
from ..models.patient_highlight_model import PatientHighlight
from ..schemas.patient_highlight import PatientHighlightCreate, PatientHighlightUpdate
from datetime import datetime
from fastapi import HTTPException

def get_all_highlights(db: Session):
    return db.query(PatientHighlight).filter(PatientHighlight.IsDeleted == "0").all()

def get_highlights_by_patient(db: Session, patient_id: int):
    return (
        db.query(PatientHighlight)
        .filter(PatientHighlight.PatientId == patient_id, PatientHighlight.IsDeleted == "0")
        .all()
    )

def create_highlight(db: Session, highlight_data: PatientHighlightCreate, created_by: int):
    db_highlight = PatientHighlight(
        **highlight_data.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return db_highlight

def update_highlight(db: Session, highlight_id: int, highlight_data: PatientHighlightUpdate, modified_by: int):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.Id == highlight_id).first()

    if not db_highlight or db_highlight.IsDeleted == "1":
        raise HTTPException(status_code=404, detail="Highlight not found")

    for key, value in highlight_data.model_dump(exclude_unset=True).items():
        setattr(db_highlight, key, value)

    db_highlight.ModifiedDate = datetime.now()
    db_highlight.ModifiedById = modified_by
    db.commit()
    db.refresh(db_highlight)
    return db_highlight

def delete_highlight(db: Session, highlight_id: int, modified_by: int):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.Id == highlight_id).first()

    if not db_highlight or db_highlight.IsDeleted == "1":
        raise HTTPException(status_code=404, detail="Highlight not found")

    db_highlight.IsDeleted = "1"
    db_highlight.ModifiedDate = datetime.now()
    db_highlight.ModifiedById = modified_by
    db.commit()
    return db_highlight
