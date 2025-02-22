from sqlalchemy.orm import Session
from ..models.patient_list_diet_model import PatientDietList
from ..schemas.patient_list_diet import PatientDietListTypeCreate, PatientDietListTypeUpdate
from datetime import datetime


def get_all_diet_types(db: Session):
    return db.query(PatientDietList).filter(PatientDietList.IsDeleted == "0").all()


def get_diet_type_by_id(db: Session, diet_type_id: int):
    return (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id,PatientDietList.IsDeleted == "0")
        .first()
    )

def create_diet_type(db: Session, diet_type: PatientDietListTypeCreate, created_by: int):
    db_diet_type = PatientDietList(
        **diet_type.model_dump(), CreatedById=created_by, ModifiedById=created_by
    )
    db.add(db_diet_type)
    db.commit()
    db.refresh(db_diet_type)
    return db_diet_type


def update_diet_type(
    db: Session, diet_type_id: int, diet_type: PatientDietListTypeUpdate, modified_by: int
):
    db_diet_type = (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id)
        .first()
    )

    if db_diet_type:
        for key, value in diet_type.model_dump(exclude_unset=True).items():
            setattr(db_diet_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_diet_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_diet_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_diet_type)
        return db_diet_type
    return None


def delete_diet_type(db: Session, diet_type_id: int, modified_by: int):
    db_diet_type = (
        db.query(PatientDietList)
        .filter(PatientDietList.Id == diet_type_id)
        .first()
    )

    if db_diet_type:
        # Soft delete by marking the record as inactive
        db_diet_type.IsDeleted = "1"
        db_diet_type.UpdatedDateTime = datetime.now()
        db_diet_type.ModifiedById = modified_by
        db.commit()
        return db_diet_type
    return None
