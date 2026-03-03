from datetime import datetime
from sqlalchemy.orm import Session

from ..logger.logger_utils import serialize_data, log_crud_action, ActionType
from ..models.patient_list_occupation_model import PatientOccupationList
from ..schemas.patient_list_occupation import PatientOccupationListTypeCreate, PatientOccupationListTypeUpdate


def get_all_occupation_types(db: Session):
    return db.query(PatientOccupationList).filter(PatientOccupationList.IsDeleted == "0").all()


def get_occupation_type_by_id(db: Session, occupation_type_id: int):
    return (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id,PatientOccupationList.IsDeleted == "0")
        .first()
    )

def create_occupation_type(db: Session, occupation_type: PatientOccupationListTypeCreate, created_by: int):
    db_occupation_type = PatientOccupationList(
        **occupation_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(occupation_type.model_dump())
    db.add(db_occupation_type)
    db.commit()
    db.refresh(db_occupation_type)

    log_crud_action(
        action=ActionType.CREATE,
        user="1",
        user_full_name="None",
        message=f"Created occupation: {db_occupation_type.Value}",
        table="PatientListOccupation",
        entity_id=db_occupation_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="config_patient_list",
    )
    return db_occupation_type


def update_occupation_type(
    db: Session, occupation_type_id: int, occupation_type: PatientOccupationListTypeUpdate, modified_by: str
):
    db_occupation_type = (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id)
        .first()
    )

    if db_occupation_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_occupation_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        for key, value in occupation_type.model_dump(exclude_unset=True).items():
            setattr(db_occupation_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_occupation_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_occupation_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_occupation_type)

        updated_data_dict = serialize_data(occupation_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user="1",
            user_full_name="None",
            table="PatientListOccupation",
            message=f"Updated occupation: {db_occupation_type.Value}",
            entity_id=db_occupation_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="config_patient_list",
        )
        return db_occupation_type
    return None


def delete_occupation_type(db: Session, occupation_type_id: int, modified_by: str):
    db_occupation_type = (
        db.query(PatientOccupationList)
        .filter(PatientOccupationList.Id == occupation_type_id)
        .first()
    )

    if db_occupation_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_occupation_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        # Soft delete by marking the record as inactive
        db_occupation_type.IsDeleted = "1"
        db_occupation_type.UpdatedDateTime = datetime.now()
        db_occupation_type.ModifiedById = modified_by
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user="1",
            user_full_name="None",
            table="PatientListOccupation",
            message=f"Deleted occupation: {db_occupation_type.Value}",
            entity_id=db_occupation_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="config_patient_list",
        )
        return db_occupation_type
    return None
