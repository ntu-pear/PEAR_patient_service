from sqlalchemy.orm import Session
from ..models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping
from ..schemas.patient_guardian_relationship_mapping import PatientGuardianRelationshipMappingCreate, PatientGuardianRelationshipMappingUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

user="1"

def get_relationship_mapping(db: Session, id: int):
    return db.query(PatientGuardianRelationshipMapping).filter(
        PatientGuardianRelationshipMapping.id == id,
        PatientGuardianRelationshipMapping.isDeleted == "0" 
    ).first()

def get_relationshipId_by_relationshipName(db: Session, relationshipName: str):
    return db.query(PatientGuardianRelationshipMapping).filter(
        PatientGuardianRelationshipMapping.relationshipName == relationshipName,
        PatientGuardianRelationshipMapping.isDeleted == "0" 
    ).first()

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
        user=user,
        user_full_name=user,
        table="PatientGuardianRelationshipMapping",
        entity_id=db_relationship.id,
        original_data=None,
        updated_data=updated_data_dict,
        message=f"Guardian relationship created: {db_relationship.relationshipName}",
        is_system_config=True,
        log_type="system",
    )
    return db_relationship

def update_relationship_mapping(
    db: Session, id: int, relationship: PatientGuardianRelationshipMappingUpdate):
    db_relationship = (
        db.query(PatientGuardianRelationshipMapping)
        .filter(
            PatientGuardianRelationshipMapping.id == id,
            PatientGuardianRelationshipMapping.isDeleted == "0" # <<< CHANGED
        )
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

        old_relationship_name = db_relationship.relationshipName

        db.commit()
        db.refresh(db_relationship)

        updated_data_dict = serialize_data(relationship.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=user,
            user_full_name=user,
            table="PatientGuardianRelationshipMapping",
            entity_id=db_relationship.id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            message=f"Guardian relationship updated: {old_relationship_name} -> {db_relationship.relationshipName}",
            is_system_config=True,
            log_type="system",
        )
    return db_relationship

def delete_relationship_mapping(db: Session, id: int):
    db_relationship = (
        db.query(PatientGuardianRelationshipMapping)
        .filter(
            PatientGuardianRelationshipMapping.id == id,
            PatientGuardianRelationshipMapping.isDeleted == "0" # <<< CHANGED
        )
        .first()
    )

    if db_relationship:
        try:
            original_data_dict = {
                k: serialize_data(v) for k, v in db_relationship.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        old_relationship_name = db_relationship.relationshipName

        setattr(db_relationship, "isDeleted", "1")
        db.commit()

        log_crud_action(
            action=ActionType.DELETE,
            user_full_name=user,
            user=user,
            table="PatientGuardianRelationshipMapping",
            entity_id=id,
            original_data=original_data_dict,
            updated_data=None,
            message=f"Guardian relationship deleted: {old_relationship_name}",
            is_system_config=True,
            log_type="system",
        )
    return db_relationship