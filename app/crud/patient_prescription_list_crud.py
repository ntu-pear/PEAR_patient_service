from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..logger.logger_utils import ActionType, log_crud_action, serialize_data
from ..models.patient_prescription_list_model import PatientPrescriptionList
from ..schemas.patient_prescription_list import (
    PatientPrescriptionListCreate,
    PatientPrescriptionListUpdate,
)


def get_prescription_lists(db: Session, pageNo: int = 0, pageSize: int = 100):
    """Get all prescription list items with pagination"""
    query = db.query(PatientPrescriptionList)
    
    totalRecords = query.count()
    totalPages = (totalRecords + pageSize - 1) // pageSize if pageSize > 0 else 0
    
    offset = pageNo * pageSize
    db_prescription_lists = query.order_by(PatientPrescriptionList.Id.desc()).offset(offset).limit(pageSize).all()
    
    return db_prescription_lists, totalRecords, totalPages

def get_prescription_list_by_id(db: Session, prescription_list_id: int):
    """Get a specific prescription list item by ID"""
    return db.query(PatientPrescriptionList).filter(
        PatientPrescriptionList.Id == prescription_list_id
    ).first()

def create_prescription_list(
    db: Session, 
    prescription_list: PatientPrescriptionListCreate,
    created_by: str,
    user_full_name: str
):
    # Check for existing prescription list with same Prescription List Value
    existing_prescription_list = db.query(PatientPrescriptionList).filter(
        PatientPrescriptionList.Value == prescription_list.Value,
        PatientPrescriptionList.IsDeleted == '0').first()
    
    if existing_prescription_list:
        raise HTTPException(status_code=400, detail="A prescription list with this name already exists")
    
    try:
        
        """Create a new prescription list item"""
        db_prescription_list = PatientPrescriptionList(**prescription_list.model_dump())
        updated_data_dict = serialize_data(prescription_list.model_dump())
        db.add(db_prescription_list)
        db.commit()
        db.refresh(db_prescription_list)

        log_crud_action(
            action=ActionType.CREATE,
            user=created_by,
            user_full_name=user_full_name,
            message="Created prescription list record",
            table="PatientPrescriptionList",
            entity_id=db_prescription_list.Id,
            original_data=None,
            updated_data=updated_data_dict,
        )
        return db_prescription_list
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def update_prescription_list(
    db: Session, 
    prescription_list_id: int, 
    prescription_list: PatientPrescriptionListUpdate,
    modified_by: str,
    user_full_name: str
):
    """Update an existing prescription list item"""
    db_prescription_list = db.query(PatientPrescriptionList).filter(
        PatientPrescriptionList.Id == prescription_list_id
    ).first()

    if db_prescription_list:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_prescription_list.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in prescription_list.model_dump().items():
            setattr(db_prescription_list, key, value)
        
        db.commit()
        db.refresh(db_prescription_list)

        updated_data_dict = serialize_data(prescription_list.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Updated prescription list record",
            table="PatientPrescriptionList",
            entity_id=db_prescription_list.Id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )
    return db_prescription_list

def delete_prescription_list(
    db: Session, 
    prescription_list_id: int,
    modified_by: str,
    user_full_name: str
):
    """Soft delete a prescription list item by setting IsDeleted to True"""
    db_prescription_list = db.query(PatientPrescriptionList).filter(
        PatientPrescriptionList.Id == prescription_list_id
    ).first()
    
    if db_prescription_list:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_prescription_list.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        db_prescription_list.IsDeleted = True
        db.commit()
        db.refresh(db_prescription_list)

        log_crud_action(
            action=ActionType.DELETE,
            user=modified_by,
            user_full_name=user_full_name,
            message="Soft deleted prescription list record",
            table="PatientPrescriptionList",
            entity_id=prescription_list_id,
            original_data=original_data_dict,
            updated_data={"IsDeleted": True}
        )
    return db_prescription_list