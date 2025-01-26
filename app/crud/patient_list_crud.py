from sqlalchemy.orm import Session
from ..models.patient_list_model import PatientList
from ..schemas.patient_list import PatientListCreate, PatientListUpdate

def get_all_list_types(db: Session):
    return db.query(PatientList).all()

def get_list(db: Session, list_type: str, item_id: int = None):
    query = db.query(PatientList).filter(PatientList.list_type == list_type)
    if item_id:
        query = query.filter(PatientList.id == item_id)
    return query.all()

def create_list_item(db: Session, list_item: PatientListCreate):
    db_list_item = PatientList(**list_item.model_dump())
    db.add(db_list_item)
    db.commit()
    db.refresh(db_list_item)
    return db_list_item

def update_list_item(db: Session, item_id: int, list_item: PatientListUpdate):
    db_list_item = db.query(PatientList).filter(PatientList.id == item_id).first()
    if db_list_item:
        for key, value in list_item.model_dump().items():
            setattr(db_list_item, key, value)
        db.commit()
        db.refresh(db_list_item)
    return db_list_item

def delete_list_item(db: Session, item_id: int):
    db_list_item = db.query(PatientList).filter(PatientList.id == item_id).first()
    if db_list_item:
        db.delete(db_list_item)
        db.commit()
    return db_list_item
