from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_highlight_type_crud as crud_highlight_type
from ..schemas.patient_highlight_type import HighlightType, HighlightTypeCreate, HighlightTypeUpdate

router = APIRouter()

@router.get("/get_highlight_types", response_model=list[HighlightType], description="Get all highlight types.")
def get_highlight_types(db: Session = Depends(get_db)):
    return crud_highlight_type.get_all_highlight_types(db)

@router.get("/get_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Get highlight type by ID.")
def get_highlight_type(highlight_type_id: int, db: Session = Depends(get_db)):
    db_highlight_type = crud_highlight_type.get_highlight_type_by_id(db, highlight_type_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type

@router.post("/create_highlight_type", response_model=HighlightType)
def create_highlight_type(highlight_type: HighlightTypeCreate, db: Session = Depends(get_db)): 
    # TODO: change user_id to current user
    user_id = "1"
    return crud_highlight_type.create_highlight_type(db, highlight_type, user_id)

@router.put("/update_highlight_type/{highlight_type_id}", response_model=HighlightType)
def update_highlight_type(highlight_type_id: int, highlight_type: HighlightTypeUpdate, db: Session = Depends(get_db)): 
    # TODO: change user_id to current user
    user_id = "1"
    db_highlight_type = crud_highlight_type.update_highlight_type(db, highlight_type_id, highlight_type, user_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type

@router.delete("/delete_highlight_type/{highlight_type_id}", response_model=HighlightType, description="Soft delete a highlight type by marking it as IsDeleted '1'")
def delete_highlight_type(highlight_type_id: int, db: Session = Depends(get_db)):  
    # TODO: change user_id to current user
    user_id = "1"
    db_highlight_type = crud_highlight_type.delete_highlight_type(db, highlight_type_id, user_id)
    if not db_highlight_type:
        raise HTTPException(status_code=404, detail="Highlight type not found")
    return db_highlight_type
