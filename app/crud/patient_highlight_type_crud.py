from sqlalchemy.orm import Session
from ..models.patient_highlight_type_model import HighlightType
from ..schemas.patient_highlight_type import HighlightTypeCreate, HighlightTypeUpdate
from datetime import datetime
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

def get_all_highlight_types(db: Session):
    return db.query(HighlightType).filter(HighlightType.IsDeleted == "0").all()

def get_highlight_type_by_id(db: Session, highlight_type_id: int):
    return (
        db.query(HighlightType)
        .filter(HighlightType.HighlightTypeID == highlight_type_id, HighlightType.IsDeleted == "0")
        .first()
    )

def create_highlight_type(
    db: Session, highlight_type: HighlightTypeCreate, created_by: int
):
    db_highlight_type = HighlightType(
        **highlight_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(highlight_type.model_dump())
    db.add(db_highlight_type)
    db.commit()
    db.refresh(db_highlight_type)

    log_crud_action(
        action=ActionType.CREATE,
        user=created_by,
        table="HighlightType",
        entity_id=db_highlight_type.HighlightTypeID,
        original_data=None,
        updated_data=updated_data_dict,
    )  
    return db_highlight_type

def update_highlight_type(
    db: Session,
    highlight_type_id: int,
    highlight_type: HighlightTypeUpdate,
    modified_by: int,
):
    db_highlight_type = (
        db.query(HighlightType)
        .filter(HighlightType.HighlightTypeID == highlight_type_id)
        .first()
    )

    if db_highlight_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_highlight_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        # Update other fields from the request body
        for key, value in highlight_type.model_dump(exclude_unset=True).items():
            setattr(db_highlight_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_highlight_type.UpdatedDateTime = datetime.now()

        # Update the ModifiedById field
        db_highlight_type.ModifiedById = modified_by

        # Commit and refresh the object
        db.commit()
        db.refresh(db_highlight_type)

        updated_data_dict = serialize_data(highlight_type.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            table="HighlightType",
            entity_id=highlight_type_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
        )
        return db_highlight_type
    return None

def delete_highlight_type(db: Session, highlight_type_id: int, modified_by: int):
    db_highlight_type = (
        db.query(HighlightType)
        .filter(HighlightType.HighlightTypeID == highlight_type_id)
        .first()
    )

    if db_highlight_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_highlight_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_highlight_type, "IsDeleted", "1")
        db_highlight_type.ModifiedById = modified_by

        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            table="HighlightType",
            entity_id=highlight_type_id,
            original_data=original_data_dict,
            updated_data=None,
        )
        return db_highlight_type
    return None
