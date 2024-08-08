from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_highlight_crud as crud_highlight
from ..schemas import patient_highlight as schemas_highlight

router = APIRouter()

@router.get("/Highlight/list", response_model=list[schemas_highlight.Highlight])
def get_highlights_grouped_by_patient(db: Session = Depends(get_db)):
    return crud_highlight.get_highlights_grouped_by_patient(db)

@router.get("/Highlight", response_model=list[schemas_highlight.Highlight])
def get_highlights(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_highlight.get_highlights(db, skip=skip, limit=limit)

@router.get("/Highlight/{highlight_id}", response_model=schemas_highlight.Highlight)
def get_highlight(highlight_id: int, db: Session = Depends(get_db)):
    db_highlight = crud_highlight.get_highlight(db, highlight_id)
    if not db_highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return db_highlight

@router.post("/Highlight/add", response_model=schemas_highlight.Highlight)
def create_highlight(highlight: schemas_highlight.HighlightCreate, db: Session = Depends(get_db)):
    return crud_highlight.create_highlight(db, highlight)

@router.put("/Highlight/update", response_model=schemas_highlight.Highlight)
def update_highlight(highlight_id: int, highlight: schemas_highlight.HighlightUpdate, db: Session = Depends(get_db)):
    db_highlight = crud_highlight.update_highlight(db, highlight_id, highlight)
    if not db_highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return db_highlight

@router.put("/Highlight/delete", response_model=schemas_highlight.Highlight)
def delete_highlight(highlight_id: int, db: Session = Depends(get_db)):
    db_highlight = crud_highlight.delete_highlight(db, highlight_id)
    if not db_highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return db_highlight
