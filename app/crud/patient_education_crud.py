from sqlalchemy.orm import Session
from ..models.patient_education_list_model import PatientEducationList
from ..schemas.patient_education_list import PatientEducationListCreate, PatientEducationListUpdate


def get_all_education_types(db: Session):
    return db.query(PatientEducationList).filter(PatientEducationList.IsDeleted == "0").all()


def get_education_type_by_id(db: Session, education_type_id: int):
    return (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id,PatientEducationList.IsDeleted == "0")
        .first()
    )

def create_education_type(db: Session, education_type: PatientEducationListCreate):
    db_education_type = PatientEducationList(
        **education_type.model_dump()
    )
    db.add(db_education_type)
    db.commit()
    db.refresh(db_education_type)
    return db_education_type


def update_education_type(
    db: Session, education_type_id: int, education_type: PatientEducationListUpdate
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

        db.commit()
        db.refresh(db_education_type)
        return db_education_type
    return None


def delete_education_type(db: Session, education_type_id: int):
    db_education_type = (
        db.query(PatientEducationList)
        .filter(PatientEducationList.Id == education_type_id)
        .first()
    )

    if db_education_type:
        # Soft delete by marking the record as inactive
        db_education_type.IsDeleted = "1"
        db_education_type.UpdatedDateTime = datetime.now()
        db.commit()
        return db_education_type
    return None
