from sqlalchemy.orm import Session
from ..models.patient_highlight_model import PatientHighlight
from ..schemas.patient_highlight import HighlightCreate, HighlightUpdate

def get_highlights(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PatientHighlight).offset(skip).limit(limit).all()

def get_highlight(db: Session, highlight_id: int):
    return db.query(PatientHighlight).filter(PatientHighlight.id == highlight_id).first()

def get_highlights_grouped_by_patient(db: Session):
    return db.query(PatientHighlight).all()  # Adjust this query as needed to group by patient_id

def create_highlight(db: Session, highlight: HighlightCreate):
    db_highlight = PatientHighlight(**highlight.dict())
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return db_highlight

def update_highlight(db: Session, highlight_id: int, highlight: HighlightUpdate):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.id == highlight_id).first()
    if db_highlight:
        for key, value in highlight.dict().items():
            setattr(db_highlight, key, value)
        db.commit()
        db.refresh(db_highlight)
    return db_highlight

def delete_highlight(db: Session, highlight_id: int):
    db_highlight = db.query(PatientHighlight).filter(PatientHighlight.id == highlight_id).first()
    if db_highlight:
        db.delete(db_highlight)
        db.commit()
    return db_highlight
