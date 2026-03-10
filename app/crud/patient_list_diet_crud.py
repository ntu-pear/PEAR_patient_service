from sqlalchemy.orm import Session

from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
from ..models.patient_list_diet_model import PatientDietList
from ..schemas.patient_list_diet import PatientDietListTypeCreate, PatientDietListTypeUpdate
from datetime import datetime

SYSTEM_USER_ID = "1"

def get_all_diet_types(db: Session):
    return db.query(PatientDietList).filter(PatientDietList.IsDeleted == "0").all()


def get_diet_type_by_id(db: Session, diet_type_id: int):
    return (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id,PatientDietList.IsDeleted == "0")
        .first()
    )

def create_diet_type(db: Session, diet_type: PatientDietListTypeCreate, created_by: str):
    db_diet_type = PatientDietList(
        **diet_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(diet_type.model_dump())
    db.add(db_diet_type)
    db.commit()
    db.refresh(db_diet_type)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        user_full_name="None",
        message=f"Created diet type: {db_diet_type.Value}",
        table="PatientListDiet",
        entity_id=db_diet_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="system",
    )
    return db_diet_type


def update_diet_type(
    db: Session, diet_type_id: int, diet_type: PatientDietListTypeUpdate, modified_by: str
):
    db_diet_type = (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id)
        .first()
    )

    if db_diet_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_diet_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in diet_type.model_dump(exclude_unset=True).items():
            setattr(db_diet_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_diet_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_diet_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_diet_type)
        updated_data_dict = serialize_data(diet_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientListDiet",
            message=f"Updated diet: {db_diet_type.Value}",
            entity_id=db_diet_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="system",
        )
        return db_diet_type
    return None


def delete_diet_type(db: Session, diet_type_id: int, modified_by: str):
    db_diet_type = (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id)
        .first()
    )

    if db_diet_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_diet_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"


        # Soft delete by marking the record as inactive
        db_diet_type.IsDeleted = "1"
        db_diet_type.UpdatedDateTime = datetime.now()
        db_diet_type.ModifiedById = modified_by
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientListDiet",
            message=f"Deleted diet: {db_diet_type.Value}",
            entity_id=db_diet_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="system",
        )
        return db_diet_type
    return None
