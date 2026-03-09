from datetime import datetime
from sqlalchemy.orm import Session

from ..logger.logger_utils import serialize_data, log_crud_action, ActionType
from ..models.patient_list_livewith_model import PatientLiveWithList
from ..schemas.patient_list_livewith import PatientLiveWithListTypeCreate, PatientLiveWithListTypeUpdate


def get_all_livewith_types(db: Session):
    return db.query(PatientLiveWithList).filter(PatientLiveWithList.IsDeleted == "0").all()


def get_livewith_type_by_id(db: Session, livewith_type_id: int):
    return (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id,PatientLiveWithList.IsDeleted == "0")
        .first()
    )

def create_livewith_type(db: Session, livewith_type: PatientLiveWithListTypeCreate, created_by: int):
    db_livewith_type = PatientLiveWithList(
        **livewith_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(livewith_type.model_dump())
    db.add(db_livewith_type)
    db.commit()
    db.refresh(db_livewith_type)

    log_crud_action(
        action=ActionType.CREATE,
        user="1",
        user_full_name="None",
        message=f"Created livewith: {db_livewith_type.Value}",
        table="PatientListLiveWith",
        entity_id=db_livewith_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="system",
    )
    return db_livewith_type


def update_livewith_type(
    db: Session, livewith_type_id: int, livewith_type: PatientLiveWithListTypeUpdate, modified_by: str
):
    db_livewith_type = (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id)
        .first()
    )

    if db_livewith_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_livewith_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in livewith_type.model_dump(exclude_unset=True).items():
            setattr(db_livewith_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_livewith_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_livewith_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_livewith_type)

        updated_data_dict = serialize_data(livewith_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user="1",
            user_full_name="None",
            table="PatientListLiveWith",
            message=f"Updated livewith: {db_livewith_type.Value}",
            entity_id=db_livewith_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="system",
        )
        return db_livewith_type
    return None


def delete_livewith_type(db: Session, livewith_type_id: int, modified_by: str):
    db_livewith_type = (
        db.query(PatientLiveWithList)
        .filter(PatientLiveWithList.Id == livewith_type_id)
        .first()
    )

    if db_livewith_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_livewith_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        # Soft delete by marking the record as inactive
        db_livewith_type.IsDeleted = "1"
        db_livewith_type.UpdatedDateTime = datetime.now()
        db_livewith_type.ModifiedById = modified_by
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user="1",
            user_full_name="None",
            table="PatientListLiveWith",
            message=f"Deleted livewith: {db_livewith_type.Value}",
            entity_id=db_livewith_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="system",
        )
        return db_livewith_type
    return None
