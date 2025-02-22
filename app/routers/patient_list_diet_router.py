from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_diet_crud as crud_diet_type
from ..schemas.patient_list_diet import (
    PatientDietListType,
    PatientDietListTypeCreate,
    PatientDietListTypeUpdate
)

router = APIRouter()

@router.get("/get_diet_types", response_model=list[PatientDietListType], description="Get all diet types.")
def get_diet_types(db: Session = Depends(get_db)):
    return crud_diet_type.get_all_diet_types(db)

@router.get("/get_diet_type/{diet_type_id}", response_model=PatientDietListType, description="Get diet type by ID.")
def get_diet_type(diet_type_id: int, db: Session = Depends(get_db)):
    db_diet_type = crud_diet_type.get_diet_type_by_id(db, diet_type_id)
    if not db_diet_type:
        raise HTTPException(status_code=404, detail="Diet type not found")
    return db_diet_type

@router.post("/create_diet_type", response_model=PatientDietListTypeCreate, description="Create a new diet type.")
def create_diet_type(diet_type: PatientDietListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1
    
    return crud_diet_type.create_diet_type(db, diet_type, user_id)

@router.put("/update_diet_type/{diet_type_id}", response_model=PatientDietListTypeUpdate, description="Update a diet type by ID.")
def update_diet_type(diet_type_id: int, diet_type: PatientDietListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1

    db_diet_type = crud_diet_type.update_diet_type(db, diet_type_id, diet_type, user_id)
    if not db_diet_type:
        raise HTTPException(status_code=404, detail="Diet type not found")
    return db_diet_type

@router.delete("/delete_diet_type/{diet_type_id}", response_model=PatientDietListType, description = "Soft delete a diet type by marking it as active '0'")
def delete_diet_type(diet_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = 1

    db_diet_type = crud_diet_type.delete_diet_type(db, diet_type_id ,user_id)
    if not db_diet_type:
        raise HTTPException(status_code=404, detail="Diet type not found")
    return db_diet_type
