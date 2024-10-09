from sqlalchemy.orm import Session
from ..models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping
from ..schemas.patient_guardian_relationship_mapping import PatientGuardianRelationshipMappingCreate, PatientGuardianRelationshipMappingUpdate


def get_relationship_mapping(db: Session, id: int):
    return db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.id == id).first()

def get_relationshipId_by_relationshipName(db: Session, relationshipName: str):
    return db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.relationshipName == relationshipName).first()

def create_relationship_mapping(db: Session, relationship: PatientGuardianRelationshipMappingCreate):
    db_relationship = PatientGuardianRelationshipMapping(**relationship.dict())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship

def update_relationship_mapping(db: Session, id: int, relationship: PatientGuardianRelationshipMappingUpdate):
    db_relationship = db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.id == id).first()
    if db_relationship:
        for key, value in relationship.dict().items():
            setattr(db_relationship, key, value)
        db.commit()
        db.refresh(db_relationship)
    return db_relationship

def delete_relationship_mapping(db: Session, id: int):
    db_relationship = db.query(PatientGuardianRelationshipMapping).filter(PatientGuardianRelationshipMapping.id == id).first()
    if db_relationship:
        setattr(db_relationship, "isDeleted", "1")
        db.commit()
    return db_relationship
