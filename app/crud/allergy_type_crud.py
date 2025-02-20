from sqlalchemy.orm import Session
from ..models.allergy_type_model import AllergyType
from ..schemas.allergy_type import AllergyTypeCreate, AllergyTypeUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_allergy_types(db: Session):
    return db.query(AllergyType).filter(AllergyType.IsDeleted == "0").all()


def get_allergy_type_by_id(db: Session, allergy_type_id: int):
    return (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id,AllergyType.IsDeleted == "0")
        .first()
    )

def create_allergy_type(db: Session, allergy_type: AllergyTypeCreate, created_by: str):
    db_allergy_type = AllergyType(
        **allergy_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    
    updated_data_dict = serialize_data(allergy_type.model_dump())
    db.add(db_allergy_type)
    db.commit()
    db.refresh(db_allergy_type)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        table="AllergyType",
        entity_id=db_allergy_type.AllergyTypeID,
        original_data=None,
        updated_data=updated_data_dict,
    )
    return db_allergy_type


def update_allergy_type(
    db: Session, allergy_type_id: int, allergy_type: AllergyTypeUpdate, modified_by: str
):
    db_allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id)
        .first()
    )

    if db_allergy_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_allergy_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        for key, value in allergy_type.model_dump(exclude_unset=True).items():
            setattr(db_allergy_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_allergy_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_allergy_type.ModifiedById = modified_by
        db.commit()
        db.refresh(db_allergy_type)

        updated_data_dict = serialize_data(allergy_type.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            table="AllergyType",
            entity_id=allergy_type_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        return db_allergy_type
    return None


def delete_allergy_type(db: Session, allergy_type_id: int, modified_by: str):
    db_allergy_type = (
        db.query(AllergyType)
        .filter(AllergyType.AllergyTypeID == allergy_type_id)
        .first()
    )

    if db_allergy_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_allergy_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        # Soft delete by marking the record as inactive
        db_allergy_type.IsDeleted = "1"
        db_allergy_type.UpdatedDateTime = datetime.now()
        db_allergy_type.ModifiedById = modified_by
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            table="AllergyType",
            entity_id=allergy_type_id,
            original_data=original_data_dict,
            updated_data=None,
        )
        return db_allergy_type
    return None
