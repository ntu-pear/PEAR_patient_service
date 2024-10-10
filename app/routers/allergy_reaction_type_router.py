from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import allergy_reaction_type_crud as crud_reaction_type
from ..schemas.allergy_reaction_type import (
    AllergyReactionType,
    AllergyReactionTypeCreate,
    AllergyReactionTypeUpdate
)

router = APIRouter()

@router.get("/get_allergy_reaction_types", response_model=list[AllergyReactionType], description="Get all allergy reaction types.")
def get_allergy_reaction_types(db: Session = Depends(get_db)):
    return crud_reaction_type.get_all_reaction_types(db)

@router.get("/get_allergy_reaction_type/{allergy_reaction_type_id}", response_model=AllergyReactionType, description="Get allergy reaction type by ID.")
def get_allergy_reaction_type(allergy_reaction_type_id: int, db: Session = Depends(get_db)):
    db_reaction_type = crud_reaction_type.get_reaction_type_by_id(db, allergy_reaction_type_id)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type

@router.post("/create_allergy_reaction_types", response_model=AllergyReactionType)
def create_allergy_reaction_type(reaction_type: AllergyReactionTypeCreate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1
    
    return crud_reaction_type.create_reaction_type(db, reaction_type, user_id)

@router.put("/update_allergy_reaction_type/{reaction_type_id}", response_model=AllergyReactionType)
def update_allergy_reaction_type(reaction_type_id: int, reaction_type: AllergyReactionTypeUpdate, db: Session = Depends(get_db)): 
    #TODO: change user_id to current user
    user_id = 1

    db_reaction_type = crud_reaction_type.update_reaction_type(db, reaction_type_id, reaction_type, user_id)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type

@router.delete("/delete_allergy_reaction_type/{reaction_type_id}", response_model=AllergyReactionType)
def delete_allergy_reaction_type(reaction_type_id: int, db: Session = Depends(get_db)):  
    #TODO: change user_id to current user
    user_id = 1

    db_reaction_type = crud_reaction_type.delete_reaction_type(db, reaction_type_id,user_id)
    if not db_reaction_type:
        raise HTTPException(status_code=404, detail="Allergy reaction type not found")
    return db_reaction_type
