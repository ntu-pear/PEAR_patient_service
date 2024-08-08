from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_crud as crud_list
from ..schemas import patient_list as schemas_list

router = APIRouter()

@router.get("/GetAllListTypes", response_model=list[schemas_list.PatientList])
def get_all_list_types(db: Session = Depends(get_db)):
    return crud_list.get_all_list_types(db)

@router.get("/List", response_model=list[schemas_list.PatientList])
def get_list(list_type: str, item_id: int = None, db: Session = Depends(get_db)):
    return crud_list.get_list(db, list_type, item_id)

@router.post("/List/add", response_model=schemas_list.PatientList)
def create_list_item(list_item: schemas_list.PatientListCreate, db: Session = Depends(get_db)):
    return crud_list.create_list_item(db, list_item)

@router.put("/List/update", response_model=schemas_list.PatientList)
def update_list_item(item_id: int, list_item: schemas_list.PatientListUpdate, db: Session = Depends(get_db)):
    db_list_item = crud_list.update_list_item(db, item_id, list_item)
    if not db_list_item:
        raise HTTPException(status_code=404, detail="List item not found")
    return db_list_item

@router.delete("/List/delete", response_model=schemas_list.PatientList)
def delete_list_item(item_id: int, db: Session = Depends(get_db)):
    db_list_item = crud_list.delete_list_item(db, item_id)
    if not db_list_item:
        raise HTTPException(status_code=404, detail="List item not found")
    return db_list_item
