from sqlalchemy.orm import Session
from ..models.patient_religion_list_model import PatientReligionList
from ..schemas.patient_religion_list import PatientReligionListCreate, PatientReligionListUpdate


def get_all_religion_types(db: Session):
    return db.query(PatientReligionList).filter(PatientReligionList.IsDeleted == "0").all()


def get_religion_type_by_id(db: Session, religion_type_id: int):
    return (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id,PatientReligionList.IsDeleted == "0")
        .first()
    )

def create_religion_type(db: Session, religion_type: PatientReligionListCreate):
    db_religion_type = PatientReligionList(
        **religion_type.model_dump()
    )
    db.add(db_religion_type)
    db.commit()
    db.refresh(db_religion_type)
    return db_religion_type


def update_religion_type(
    db: Session, religion_type_id: int, religion_type: PatientReligionListUpdate
):
    db_religion_type = (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id)
        .first()
    )

    if db_religion_type:
        for key, value in religion_type.model_dump(exclude_unset=True).items():
            setattr(db_religion_type, key, value)

        # Set UpdatedDateTime to the current datetime
        db_religion_type.UpdatedDateTime = datetime.now()

        db.commit()
        db.refresh(db_religion_type)
        return db_religion_type
    return None


def delete_religion_type(db: Session, religion_type_id: int):
    db_religion_type = (
        db.query(PatientReligionList)
        .filter(PatientReligionList.Id == religion_type_id)
        .first()
    )

    if db_religion_type:
        # Soft delete by marking the record as inactive
        db_religion_type.IsDeleted = "1"
        db_religion_type.UpdatedDateTime = datetime.now()
        db.commit()
        return db_religion_type
    return None
