from sqlalchemy.orm import Session
from ..models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping
from ..schemas.patient_guardian_relationship_mapping import PatientGuardianRelationshipMappingCreate, PatientGuardianRelationshipMappingUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

user=1

def get_relationship_mapping(db: Session, id: int):
    return db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.id == id).first()

def get_relationshipId_by_relationshipName(db: Session, relationshipName: str):
    return db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.relationshipName == relationshipName).first()

def create_relationship_mapping(
        db: Session, relationship: PatientGuardianRelationshipMappingCreate
):
    db_relationship = PatientGuardianRelationshipMapping(**relationship.model_dump())
    updated_data_dict = serialize_data(relationship.model_dump())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)

    log_crud_action(
        action=ActionType.CREATE,
        user=1,
        table="PatientGuardianRelationshipMapping",
        entity_id=db_relationship.id,
        original_data=None,
        updated_data=updated_data_dict
    )
    return db_relationship

def update_relationship_mapping(
        db: Session, id: int, relationship: PatientGuardianRelationshipMappingUpdate
):
    db_relationship = (
        db.query(PatientGuardianRelationshipMapping)
        .filter(PatientGuardianRelationshipMapping.id == id)
        .first()
    )

    if db_relationship:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_relationship.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in relationship.model_dump().items():
            setattr(db_relationship, key, value)

        db.commit()
        db.refresh(db_relationship)

        updated_data_dict = serialize_data(relationship.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=user,
            table="PatientGuardianRelationshipMapping",
            entity_id=db_relationship.id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )
    return db_relationship

def delete_relationship_mapping(db: Session, id: int):
    db_relationship = (
        db.query(PatientGuardianRelationshipMapping)
        .filter(PatientGuardianRelationshipMapping.id == id)
        .first()
    )

    if db_relationship:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_relationship.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_relationship, "isDeleted", "1")
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user=user,
            table="PatientGuardianRelationshipMapping",
            entity_id=id,
            original_data=original_data_dict,
            updated_data=None
        )
    return db_relationship
