from datetime import datetime
from sqlalchemy.orm import Session

from ..logger.logger_utils import serialize_data, log_crud_action, ActionType
from ..models.patient_list_religion_model import PatientReligionList
from ..schemas.patient_list_religion import PatientReligionListTypeCreate, PatientReligionListTypeUpdate


def get_all_religion_types(db: Session):
    return db.query(PatientReligionList).filter(PatientReligionList.IsDeleted == "0").all()


def get_religion_type_by_id(db: Session, religion_type_id: int):
    return (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id,PatientReligionList.IsDeleted == "0")
        .first()
    )

def create_religion_type(db: Session, religion_type: PatientReligionListTypeCreate, created_by: int):
    db_religion_type = PatientReligionList(
        **religion_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(religion_type.model_dump())
    db.add(db_religion_type)
    db.commit()
    db.refresh(db_religion_type)
    log_crud_action(
        action=ActionType.CREATE,
        user="1",
        user_full_name="None",
        message=f"Created religion: {db_religion_type.Value}",
        table="PatientListReligion",
        entity_id=db_religion_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="system",
    )
    return db_religion_type


def update_religion_type(
    db: Session, religion_type_id: int, religion_type: PatientReligionListTypeUpdate, modified_by: str
):
    db_religion_type = (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id)
        .first()
    )

    if db_religion_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_religion_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        for key, value in religion_type.model_dump(exclude_unset=True).items():
            setattr(db_religion_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_religion_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_religion_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_religion_type)

        updated_data_dict = serialize_data(religion_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user="1",
            user_full_name="None",
            table="PatientListReligion",
            message=f"Updated religion: {db_religion_type.Value}",
            entity_id=db_religion_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="system",
        )
        return db_religion_type
    return None


def delete_religion_type(db: Session, religion_type_id: int, modified_by: str):
    db_religion_type = (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id)
        .first()
    )

    if db_religion_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_religion_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        # Soft delete by marking the record as inactive
        db_religion_type.IsDeleted = "1"
        db_religion_type.UpdatedDateTime = datetime.now()
        db_religion_type.ModifiedById = modified_by
        db.commit()
        log_crud_action(
            action=ActionType.DELETE,
            user="1",
            user_full_name="None",
            table="PatientListReligion",
            message=f"Deleted religion: {db_religion_type.Value}",
            entity_id=db_religion_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="system",
        )
        return db_religion_type
    return None
