from datetime import datetime
from sqlalchemy.orm import Session

from ..logger.logger_utils import serialize_data, log_crud_action, ActionType
from ..models.patient_list_education_model import PatientEducationList
from ..schemas.patient_list_education import PatientEducationListTypeCreate, PatientEducationListTypeUpdate

SYSTEM_USER_ID = "1"
def get_all_education_types(db: Session):
    return db.query(PatientEducationList).filter(PatientEducationList.IsDeleted == "0").all()


def get_education_type_by_id(db: Session, education_type_id: int):
    return (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id,PatientEducationList.IsDeleted == "0")
        .first()
    )

def create_education_type(db: Session, education_type: PatientEducationListTypeCreate, created_by: int):
    db_education_type = PatientEducationList(
        **education_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(education_type.model_dump())
    db.add(db_education_type)
    db.commit()
    db.refresh(db_education_type)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        user_full_name="None",
        message=f"Created education type: {db_education_type.Value}",
        table="PatientListEducation",
        entity_id=db_education_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="system",
    )
    return db_education_type


def update_education_type(
    db: Session, education_type_id: int, education_type: PatientEducationListTypeUpdate, modified_by: str
):
    db_education_type = (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id)
        .first()
    )

    if db_education_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_education_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        for key, value in education_type.model_dump(exclude_unset=True).items():
            setattr(db_education_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_education_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_education_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_education_type)

        updated_data_dict = serialize_data(education_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientListEducation",
            message=f"Updated education: {db_education_type.Value}",
            entity_id=db_education_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="system",
        )
        return db_education_type
    return None


def delete_education_type(db: Session, education_type_id: int, modified_by: str):
    db_education_type = (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id)
        .first()
    )

    if db_education_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_education_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        # Soft delete by marking the record as inactive
        db_education_type.IsDeleted = "1"
        db_education_type.UpdatedDateTime = datetime.now()
        db_education_type.ModifiedById = modified_by
        db.commit()
        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientListEducation",
            message=f"Deleted education: {db_education_type.Value}",
            entity_id=db_education_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="system",
        )
        return db_education_type
    return None
