from sqlalchemy.orm import Session
from ..models.patient_list_model import PatientList
from ..schemas.patient_list import PatientListCreate, PatientListUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

SYSTEM_USER_ID = "1"

def get_all_list_types(db: Session):
    return db.query(PatientList).all()

def get_list(db: Session, list_type: str, item_id: int = None):
    query = db.query(PatientList).filter(PatientList.type == list_type)
    if item_id:
        query = query.filter(PatientList.id == item_id)
    return query.all()

def create_list_item(db: Session, list_item: PatientListCreate):
    db_list_item = PatientList(**list_item.model_dump())
    updated_data_dict = serialize_data(list_item.model_dump())
    db.add(db_list_item)
    db.commit()
    db.refresh(db_list_item)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        user_full_name="None",
        message=f"Created list item: {db_list_item.value} ({db_list_item.type})",
        table="PatientList",
        entity_id=db_list_item.id,
        original_data=None,
        updated_data=updated_data_dict,
        is_system_config=True,
        log_type="system",
    )
    return db_list_item

def update_list_item(
    db: Session, 
    item_id: int, 
    list_item: PatientListUpdate
):
    db_list_item = (
        db.query(PatientList)
        .filter(PatientList.id == item_id)
        .first()
    )

    if db_list_item:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_list_item.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in list_item.model_dump().items():
            setattr(db_list_item, key, value)
        db.commit()
        db.refresh(db_list_item)

        updated_data_dict = serialize_data(list_item.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientList",
            message=f"Updated list item: {db_list_item.value}",
            entity_id=db_list_item.id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            is_system_config=True,
            log_type="system",
        )
    return db_list_item

def delete_list_item(db: Session, item_id: int):
    db_list_item = db.query(PatientList).filter(PatientList.id == item_id).first()
    if db_list_item:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_list_item.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        db.delete(db_list_item)
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            user_full_name="None",
            table="PatientList",
            message=f"Deleted list item: {db_list_item.value}",
            entity_id=item_id,
            original_data=original_data_dict,
            updated_data=None,
            is_system_config=True,
            log_type="system",
        )
    return db_list_item
