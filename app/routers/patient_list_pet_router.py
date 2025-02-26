from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_pet_crud as crud_pet_type
from ..schemas.patient_list_pet import (
    PatientPetListType,
    PatientPetListTypeCreate,
    PatientPetListTypeUpdate
)

router = APIRouter()

@router.get("/get_pet_types", response_model=list[PatientPetListType], description="Get all pet types.")
def get_pet_types(db: Session = Depends(get_db)):
    return crud_pet_type.get_all_pet_types(db)

@router.get("/get_pet_type/{pet_type_id}", response_model=PatientPetListType, description="Get pet type by ID.")
def get_pet_type(pet_type_id: int, db: Session = Depends(get_db)):
    db_pet_type = crud_pet_type.get_pet_type_by_id(db, pet_type_id)
    if not db_pet_type:
        raise HTTPException(status_code=404, detail="Pet type not found")
    return db_pet_type

@router.post("/create_pet_type", response_model=PatientPetListTypeCreate, description="Create a new pet type.")
def create_pet_type(pet_type: PatientPetListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1
    
    return crud_pet_type.create_pet_type(db, pet_type, user_id)

@router.put("/update_pet_type/{pet_type_id}", response_model=PatientPetListTypeUpdate, description="Update a pet type by ID.")
def update_pet_type(pet_type_id: int, pet_type: PatientPetListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1

    db_pet_type = crud_pet_type.update_pet_type(db, pet_type_id, pet_type, user_id)
    if not db_pet_type:
        raise HTTPException(status_code=404, detail="Pet type not found")
    return db_pet_type

@router.delete("/delete_pet_type/{pet_type_id}", response_model=PatientPetListType, description = "Soft delete an pet type by marking it as active '0'")
def delete_pet_type(pet_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = 1

    db_pet_type = crud_pet_type.delete_pet_type(db, pet_type_id ,user_id)
    if not db_pet_type:
        raise HTTPException(status_code=404, detail="Pet type not found")
    return db_pet_type
