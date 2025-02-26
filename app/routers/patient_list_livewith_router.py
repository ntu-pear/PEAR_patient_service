from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_livewith_crud as crud_livewith_type
from ..schemas.patient_list_livewith import (
    PatientLiveWithListType,
    PatientLiveWithListTypeCreate,
    PatientLiveWithListTypeUpdate
)

router = APIRouter()

@router.get("/get_livewith_types", response_model=list[PatientLiveWithListType], description="Get all livewith types.")
def get_livewith_types(db: Session = Depends(get_db)):
    return crud_livewith_type.get_all_livewith_types(db)

@router.get("/get_livewith_type/{livewith_type_id}", response_model=PatientLiveWithListType, description="Get livewith type by ID.")
def get_livewith_type(livewith_type_id: int, db: Session = Depends(get_db)):
    db_livewith_type = crud_livewith_type.get_livewith_type_by_id(db, livewith_type_id)
    if not db_livewith_type:
        raise HTTPException(status_code=404, detail="Livewith type not found")
    return db_livewith_type

@router.post("/create_livewith_type", response_model=PatientLiveWithListTypeCreate, description="Create a new livewith type.")
def create_livewith_type(livewith_type: PatientLiveWithListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"
    
    return crud_livewith_type.create_livewith_type(db, livewith_type, user_id)

@router.put("/update_livewith_type/{livewith_type_id}", response_model=PatientLiveWithListTypeUpdate, description="Update a livewith type by ID.")
def update_livewith_type(livewith_type_id: int, livewith_type: PatientLiveWithListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"

    db_livewith_type = crud_livewith_type.update_livewith_type(db, livewith_type_id, livewith_type, user_id)
    if not db_livewith_type:
        raise HTTPException(status_code=404, detail="Livewith type not found")
    return db_livewith_type

@router.delete("/delete_livewith_type/{livewith_type_id}", response_model=PatientLiveWithListType, description = "Soft delete a livewith type by marking it as active '0'")
def delete_livewith_type(livewith_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = "1"

    db_livewith_type = crud_livewith_type.delete_livewith_type(db, livewith_type_id ,user_id)
    if not db_livewith_type:
        raise HTTPException(status_code=404, detail="Livewith type not found")
    return db_livewith_type
