from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.jwt_utils import extract_jwt_payload, get_user_id
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
def create_diet_type(request: Request, diet_type: PatientDietListTypeCreate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    return crud_diet_type.create_diet_type(db, diet_type, user_id)

@router.put("/update_diet_type/{diet_type_id}", response_model=PatientDietListTypeUpdate, description="Update a diet type by ID.")
def update_diet_type(request: Request, diet_type_id: int, diet_type: PatientDietListTypeUpdate, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    db_diet_type = crud_diet_type.update_diet_type(db, diet_type_id, diet_type, user_id)
    if not db_diet_type:
        raise HTTPException(status_code=404, detail="Diet type not found")
    return db_diet_type

@router.delete("/delete_diet_type/{diet_type_id}", response_model=PatientDietListType, description="Soft delete a diet type by marking it as active '0'")
def delete_diet_type(request: Request, diet_type_id: int, db: Session = Depends(get_db), require_auth: bool = True):
    payload = extract_jwt_payload(request, require_auth)
    user_id = get_user_id(payload) or "anonymous"
    db_diet_type = crud_diet_type.delete_diet_type(db, diet_type_id, user_id)
    if not db_diet_type:
        raise HTTPException(status_code=404, detail="Diet type not found")
    return db_diet_type
