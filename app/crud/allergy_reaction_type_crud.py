from sqlalchemy.orm import Session
from ..models.allergy_reaction_type_model import AllergyReactionType
from ..schemas.allergy_reaction_type import AllergyReactionTypeCreate, AllergyReactionTypeUpdate
from datetime import datetime

def get_all_reaction_types(db: Session):
    return db.query(AllergyReactionType).all()

def get_reaction_type_by_id(db: Session, allergy_reaction_type_id: int):
    return db.query(AllergyReactionType).filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id).first()

def create_reaction_type(db: Session, reaction_type: AllergyReactionTypeCreate, created_by:int):
    db_reaction_type = AllergyReactionType(
        **reaction_type.dict(),
        createdById = created_by,
        modifiedById = created_by
    )
    db.add(db_reaction_type)
    db.commit()
    db.refresh(db_reaction_type)
    return db_reaction_type

def update_reaction_type(db: Session, allergy_reaction_type_id: int, reaction_type: AllergyReactionTypeUpdate,modified_by: int):
    db_reaction_type = db.query(AllergyReactionType).filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id).first()

    if db_reaction_type:
        # Update other fields from the request body
        for key, value in reaction_type.dict(exclude_unset=True).items():
            setattr(db_reaction_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_reaction_type.UpdatedDateTime = datetime.now()

         # Update the modifiedById field
        db_reaction_type.modifiedById = modified_by

        # Commit and refresh the object
        db.commit()
        db.refresh(db_reaction_type)
        return db_reaction_type
    return None

def delete_reaction_type(db: Session, allergy_reaction_type_id: int,modified_by: int):
    db_reaction_type = db.query(AllergyReactionType).filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id).first()

    if db_reaction_type:
        setattr(db_reaction_type, "active", "0")
        db_reaction_type.modifiedById = modified_by  

        db.commit()
        return db_reaction_type
    return None