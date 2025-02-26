from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_religion_crud as crud_religion_type
from ..schemas.patient_list_religion import (
    PatientReligionListType,
    PatientReligionListTypeCreate,
    PatientReligionListTypeUpdate
)

router = APIRouter()

@router.get("/get_religion_types", response_model=list[PatientReligionListType], description="Get all religion types.")
def get_religion_types(db: Session = Depends(get_db)):
    return crud_religion_type.get_all_religion_types(db)

@router.get("/get_religion_type/{religion_type_id}", response_model=PatientReligionListType, description="Get religion type by ID.")
def get_religion_type(religion_type_id: int, db: Session = Depends(get_db)):
    db_religion_type = crud_religion_type.get_religion_type_by_id(db, religion_type_id)
    if not db_religion_type:
        raise HTTPException(status_code=404, detail="Religion type not found")
    return db_religion_type

@router.post("/create_religion_type", response_model=PatientReligionListTypeCreate, description="Create a new religion type.")
def create_religion_type(religion_type: PatientReligionListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"
    
    return crud_religion_type.create_religion_type(db, religion_type, user_id)

@router.put("/update_religion_type/{religion_type_id}", response_model=PatientReligionListTypeUpdate, description="Update a religion type by ID.")
def update_religion_type(religion_type_id: int, religion_type: PatientReligionListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = "1"

    db_religion_type = crud_religion_type.update_religion_type(db, religion_type_id, religion_type, user_id)
    if not db_religion_type:
        raise HTTPException(status_code=404, detail="Religion type not found")
    return db_religion_type

@router.delete("/delete_religion_type/{religion_type_id}", response_model=PatientReligionListType, description = "Soft delete a religion type by marking it as active '0'")
def delete_religion_type(religion_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = "1"

    db_religion_type = crud_religion_type.delete_religion_type(db, religion_type_id ,user_id)
    if not db_religion_type:
        raise HTTPException(status_code=404, detail="Religion type not found")
    return db_religion_type
