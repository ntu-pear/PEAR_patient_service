from datetime import datetime
from sqlalchemy.orm import Session
from ..models.patient_list_education_model import PatientEducationList
from ..schemas.patient_list_education import PatientEducationListTypeCreate, PatientEducationListTypeUpdate


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
    db.add(db_education_type)
    db.commit()
    db.refresh(db_education_type)
    return db_education_type


def update_education_type(
    db: Session, education_type_id: int, education_type: PatientEducationListTypeUpdate, modified_by: int
):
    db_education_type = (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id)
        .first()
    )

    if db_education_type:
        for key, value in education_type.model_dump(exclude_unset=True).items():
            setattr(db_education_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_education_type.UpdatedDateTime = datetime.now()

        # Update the modifiedById field
        db_education_type.ModifiedById = modified_by

        db.commit()
        db.refresh(db_education_type)
        return db_education_type
    return None


def delete_education_type(db: Session, education_type_id: int, modified_by: int):
    db_education_type = (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id)
        .first()
    )

    if db_education_type:
        # Soft delete by marking the record as inactive
        db_education_type.IsDeleted = "1"
        db_education_type.UpdatedDateTime = datetime.now()
        db_education_type.ModifiedById = modified_by
        db.commit()
        return db_education_type
    return None
