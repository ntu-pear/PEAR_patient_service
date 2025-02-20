from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_list_education_crud as crud_education_type
from ..schemas.patient_list_education import (
    PatientEducationListType,
    PatientEducationListTypeCreate,
    PatientEducationListTypeUpdate
)

router = APIRouter()

@router.get("/get_education_types", response_model=list[PatientEducationListType], description="Get all education types.")
def get_education_types(db: Session = Depends(get_db)):
    return crud_education_type.get_all_education_types(db)

@router.get("/get_education_type/{education_type_id}", response_model=PatientEducationListType, description="Get education type by ID.")
def get_education_type(education_type_id: int, db: Session = Depends(get_db)):
    db_education_type = crud_education_type.get_education_type_by_id(db, education_type_id)
    if not db_education_type:
        raise HTTPException(status_code=404, detail="Education type not found")
    return db_education_type

@router.post("/create_education_type", response_model=PatientEducationListTypeCreate, description="Create a new education type.")
def create_education_type(education_type: PatientEducationListTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1
    
    return crud_education_type.create_education_type(db, education_type, user_id)

@router.put("/update_education_type/{education_type_id}", response_model=PatientEducationListTypeUpdate, description="Update an education type by ID.")
def update_education_type(education_type_id: int, education_type: PatientEducationListTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1

    db_education_type = crud_education_type.update_education_type(db, education_type_id, education_type, user_id)
    if not db_education_type:
        raise HTTPException(status_code=404, detail="Education type not found")
    return db_education_type

@router.delete("/delete_education_type/{education_type_id}", response_model=PatientEducationListType, description = "Soft delete an education type by marking it as active '0'")
def delete_education_type(education_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = 1

    db_education_type = crud_education_type.delete_education_type(db, education_type_id ,user_id)
    if not db_education_type:
        raise HTTPException(status_code=404, detail="Education type not found")
    return db_education_type
