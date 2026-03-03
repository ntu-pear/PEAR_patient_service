from datetime import datetime
from sqlalchemy.orm import Session

from ..logger.logger_utils import serialize_data, log_crud_action, ActionType
from ..models.patient_list_pet_model import PatientPetList
from ..schemas.patient_list_pet import PatientPetListTypeCreate, PatientPetListTypeUpdate


def get_all_pet_types(db: Session):
    return db.query(PatientPetList).filter(PatientPetList.IsDeleted == "0").all()


def get_pet_type_by_id(db: Session, pet_type_id: int):
    return (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id,PatientPetList.IsDeleted == "0")
        .first()
    )

def create_pet_type(db: Session, pet_type: PatientPetListTypeCreate, created_by: int):
    db_pet_type = PatientPetList(
        **pet_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    updated_data_dict = serialize_data(pet_type.model_dump())
    db.add(db_pet_type)
    db.commit()
    db.refresh(db_pet_type)

    log_crud_action(
        action=ActionType.CREATE,
        user="1",
        user_full_name="None",
        message=f"Created pet: {db_pet_type.Value}",
        table="PatientListPet",
        entity_id=db_pet_type.Id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="config_patient_list",
    )
    return db_pet_type


def update_pet_type(
    db: Session, pet_type_id: int, pet_type: PatientPetListTypeUpdate, modified_by: str
):
    db_pet_type = (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id)
        .first()
    )

    if db_pet_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_pet_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        for key, value in pet_type.model_dump(exclude_unset=True).items():
            setattr(db_pet_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_pet_type.UpdatedDateTime = datetime.now()

        # Set the ModifiedById field
        db_pet_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_pet_type)

        updated_data_dict = serialize_data(pet_type.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user="1",
            user_full_name="None",
            table="PatientListPet",
            message=f"Updated pet: {db_pet_type.Value}",
            entity_id=db_pet_type.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="config_patient_list",
        )
        return db_pet_type
    return None


def delete_pet_type(db: Session, pet_type_id: int, modified_by: str):
    db_pet_type = (
        db.query(PatientPetList)
        .filter(PatientPetList.Id == pet_type_id)
        .first()
    )

    if db_pet_type:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_pet_type.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"
        # Soft delete by marking the record as inactive
        db_pet_type.IsDeleted = "1"
        db_pet_type.UpdatedDateTime = datetime.now()
        db_pet_type.ModifiedById = modified_by
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user="1",
            user_full_name="None",
            table="PatientListPet",
            message=f"Deleted pet: {db_pet_type.Value}",
            entity_id=db_pet_type.Id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="config_patient_list",
        )
        return db_pet_type
    return None
