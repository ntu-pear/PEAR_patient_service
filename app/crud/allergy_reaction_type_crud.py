import math
from sqlalchemy.orm import Session
from ..models.allergy_reaction_type_model import AllergyReactionType
from ..schemas.allergy_reaction_type import (
    AllergyReactionTypeCreate,
    AllergyReactionTypeUpdate,
)
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_reaction_types(db: Session, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    query = db.query(
        AllergyReactionType
    ).filter(
        AllergyReactionType.IsDeleted == "0"
    )

    totalRecords = query.count()
    totalPages = math.ceil(totalRecords / pageSize)

    results = query.order_by(AllergyReactionType.AllergyReactionTypeID).offset(offset).limit(pageSize).all()

    return results, totalRecords, totalPages


def get_reaction_type_by_id(db: Session, allergy_reaction_type_id: int):
    return (
        db.query(AllergyReactionType)
        .filter(AllergyReactionType.AllergyReactionTypeID == allergy_reaction_type_id, AllergyReactionType.IsDeleted == "0")
        .first()
    )


def create_reaction_type(
    db: Session, reaction_type: AllergyReactionTypeCreate, created_by: str, user_full_name: str
):
    db_reaction_type = AllergyReactionType(
        **reaction_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(reaction_type.model_dump())
    db.add(db_reaction_type)
    db.commit()
    db.refresh(db_reaction_type)

    # Include the allergy reaction type name in the logs
    # This is a global config change (adding a new allergy type to the system), and is not patient focused
    allergy_reaction_type_name = db_reaction_type.Value if db_reaction_type else None
    
    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        user_full_name=user_full_name,
        message=f"Created allergy reaction type: {allergy_reaction_type_name}",
        table="AllergyReactionType",
        entity_id=db_reaction_type.AllergyReactionTypeID,
        original_data=None,
        updated_data=updated_data_dict,
        log_type = "system",
        is_system_config=True,
    )
    return db_reaction_type

def update_reaction_type(
    db: Session,
    allergy_reaction_type_id: int,
    reaction_type: AllergyReactionTypeUpdate,
    modified_by: str,
    user_full_name:str
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

        # Store the old reaction type name for message field in log
        old_allergy_reaction_type_name = db_reaction_type.Value

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
            user_full_name=user_full_name,
            message=f"Updated allergy reaction type: {old_allergy_reaction_type_name} -> {db_reaction_type.Value}",
            table="AllergyReactionType",
            entity_id=allergy_reaction_type_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            log_type = "system",
            is_system_config=True,
        )
        return db_reaction_type
    return None

def delete_reaction_type(db: Session, allergy_reaction_type_id: int, modified_by: str, user_full_name:str):
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

        # Capture allergy reaction name before deletion
        allergy_reaction_type_name = db_reaction_type.Value

        setattr(db_reaction_type, "IsDeleted", "1")
        db_reaction_type.ModifiedById = modified_by

        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message=f"Deleted allergy reaction type: {allergy_reaction_type_name}",
            table="AllergyReactionType",
            entity_id=allergy_reaction_type_id,
            original_data=original_data_dict,
            updated_data=None,
            log_type = "system",
            is_system_config=True,
        )
        return db_reaction_type
    return None

