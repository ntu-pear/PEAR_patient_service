from sqlalchemy.orm import Session
from ..models.allergy_reaction_type_model import AllergyReactionType
from ..schemas.allergy_reaction_type import (
    AllergyReactionTypeCreate,
    AllergyReactionTypeUpdate,
)
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_reaction_types(db: Session):
    return db.query(AllergyReactionType).filter(AllergyReactionType.IsDeleted == "0").all()


def get_reaction_type_by_id(db: Session, allergy_reaction_type_id: int):
    return (
        db.query(AllergyReactionType)
        .filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id, AllergyReactionType.IsDeleted == "0")
        .first()
    )


def create_reaction_type(
    db: Session, reaction_type: AllergyReactionTypeCreate, created_by: str
):
    db_reaction_type = AllergyReactionType(
        **reaction_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(reaction_type.model_dump())
    db.add(db_reaction_type)
    db.commit()
    db.refresh(db_reaction_type)
    
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        table="AllergyReactionType",
        entity_id=db_reaction_type.AllergyReactionTypeID,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_reaction_type

def update_reaction_type(
    db: Session,
    allergy_reaction_type_id: int,
    reaction_type: AllergyReactionTypeUpdate,
    modified_by: str,
):
    db_reaction_type = (
        db.query(AllergyReactionType)
        .filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id)
        .first()
    )

    if db_reaction_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_reaction_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in reaction_type.model_dump(exclude_unset=True).items():
            setattr(db_reaction_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_reaction_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_reaction_type.ModifiedById = modified_by

        # Commit and refresh the object
        db.commit()
        db.refresh(db_reaction_type)

        updated_data_dict = serialize_data(reaction_type.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            table="AllergyReactionType",
            entity_id=allergy_reaction_type_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        return db_reaction_type
    return None

def delete_reaction_type(db: Session, allergy_reaction_type_id: int, modified_by: str):
    db_reaction_type = (
        db.query(AllergyReactionType)
        .filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id)
        .first()
    )

    if db_reaction_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_reaction_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_reaction_type, "IsDeleted", "1")
        db_reaction_type.ModifiedById = modified_by
        setattr(db_reaction_type, "IsDeleted", "1")
        db_reaction_type.ModifiedById = modified_by

        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            table="Patient",
            entity_id=allergy_reaction_type_id,
            original_data=original_data_dict,
            updated_data=None,
        )
        return db_reaction_type
    return None

