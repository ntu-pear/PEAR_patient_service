from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import allergy_type_crud as crud_allergy_type
from ..schemas.allergy_type import (
    AllergyType,
    AllergyTypeCreate,
    AllergyTypeUpdate
)

router = APIRouter()

@router.get("/get_allergy_types", response_model=list[AllergyType], description="Get all allergy types.")
def get_allergy_types(db: Session = Depends(get_db)):
    return crud_allergy_type.get_all_allergy_types(db)

@router.get("/get_allergy_type/{allergy_type_id}", response_model=AllergyType, description="Get allergy type by ID.")
def get_allergy_type(allergy_type_id: int, db: Session = Depends(get_db)):
    db_allergy_type = crud_allergy_type.get_allergy_type_by_id(db, allergy_type_id)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type

@router.post("/create_allergy_type", response_model=AllergyTypeCreate, description="Create a new allergy type.")
def create_allergy_type(allergy_type: AllergyTypeCreate, db: Session = Depends(get_db)): 
    
    #TODO: change user_id to current user
    user_id = "1"

    return crud_allergy_type.create_allergy_type(db, allergy_type, user_id)

@router.put("/update_allergy_type/{allergy_type_id}", response_model=AllergyTypeUpdate, description="Update an allergy type.")
def update_allergy_type(allergy_type_id: int, allergy_type: AllergyTypeUpdate, db: Session = Depends(get_db)): 
    
    #TODO: change user_id to current user
    user_id = "1"

    db_allergy_type = crud_allergy_type.update_allergy_type(db, allergy_type_id, allergy_type, user_id)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type

@router.delete("/delete_allergy_type/{allergy_type_id}", response_model=AllergyType, description="Soft delete an allergy type by marking it as active '0'.")
def delete_allergy_type(allergy_type_id: int, db: Session = Depends(get_db)): 
    
    #TODO: change user_id to current user
    user_id = "1"

    db_allergy_type = crud_allergy_type.delete_allergy_type(db, allergy_type_id, user_id)
    if not db_allergy_type:
        raise HTTPException(status_code=404, detail="Allergy type not found")
    return db_allergy_type
