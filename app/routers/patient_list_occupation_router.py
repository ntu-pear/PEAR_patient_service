from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_occupation_crud as crud_occupation_type
from ..schemas.patient_list_occupation import (
    PatientOccupationListType,
    PatientOccupationListTypeCreate,
    PatientOccupationListTypeUpdate
)

router = APIRouter()

@router.get("/get_occupation_types", response_model=list[PatientOccupationListType], description="Get all occupation types.")
def get_occupation_types(db: Session = Depends(get_db)):
    return crud_occupation_type.get_all_occupation_types(db)

@router.get("/get_occupation_type/{occupation_type_id}", response_model=PatientOccupationListType, description="Get occupation type by ID.")
def get_occupation_type(occupation_type_id: int, db: Session = Depends(get_db)):
    db_occupation_type = crud_occupation_type.get_occupation_type_by_id(db, occupation_type_id)
    if not db_occupation_type:
        raise HTTPException(status_code=404, detail="Occupation type not found")
    return db_occupation_type

@router.post("/create_occupation_type", response_model=PatientOccupationListTypeCreate)
def create_occupation_type(occupation_type: PatientOccupationListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"
    
    return crud_occupation_type.create_occupation_type(db, occupation_type, user_id)

@router.put("/update_occupation_type/{occupation_type_id}", response_model=PatientOccupationListTypeUpdate)
def update_occupation_type(occupation_type_id: int, occupation_type: PatientOccupationListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"

    db_occupation_type = crud_occupation_type.update_occupation_type(db, occupation_type_id, occupation_type, user_id)
    if not db_occupation_type:
        raise HTTPException(status_code=404, detail="Occupation type not found")
    return db_occupation_type

@router.delete("/delete_occupation_type/{occupation_type_id}", response_model=PatientOccupationListType, description = "Soft delete an occupation type by marking it as active '0'")
def delete_occupation_type(occupation_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = "1"

    db_occupation_type = crud_occupation_type.delete_occupation_type(db, occupation_type_id ,user_id)
    if not db_occupation_type:
        raise HTTPException(status_code=404, detail="Occupation type not found")
    return db_occupation_type
