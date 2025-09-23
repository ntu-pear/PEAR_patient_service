from sqlalchemy.orm import Session
from ..models.patient_model import Patient
from ..models.patient_guardian_model import PatientGuardian
from ..models.patient_guardian_relationship_mapping_model import PatientGuardianRelationshipMapping
from ..models.patient_patient_guardian_model import PatientPatientGuardian
from ..schemas.patient_patient_guardian import PatientPatientGuardianCreate, PatientPatientGuardianUpdate, PatientPatientGuardianByGuardian, PatientWithRelationship as PatientWithRelationshipModel, GuardianWithRelationship as GuardianWithRelationshipModel 
from ..schemas.patient_guardian import PatientGuardian as PatientGuardianModel
from ..schemas.patient import Patient as PatientModel
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data

SYSTEM_USER_ID = "1"

def get_all_patient_guardian(db: Session, id: int, limit: int = 10):
    return db.query(PatientPatientGuardian).order_by(PatientPatientGuardian.id).limit(limit).all()

def get_all_patient_guardian_by_patientId(db: Session, patientId: int):
    patient_guardian_relationships =  db.query(PatientPatientGuardian).join(Patient).join(PatientGuardian).join(PatientGuardianRelationshipMapping).filter(PatientPatientGuardian.patientId == patientId).all()
    db_patient = PatientModel.from_orm(patient_guardian_relationships[0].patient)
    patient_guardians = []
    for row in patient_guardian_relationships:
        patient_guardian = row.patient_guardian
        relationship_name = row.relationship.relationshipName
        
        guardian_with_relationship = GuardianWithRelationshipModel(
            patient_guardian = PatientGuardianModel.from_orm(patient_guardian),  # Convert ORM patient to Pydantic model
            relationshipName=relationship_name
        )
        patient_guardians.append(guardian_with_relationship)
    response_model = {"patient": db_patient, "patient_guardians": patient_guardians}
    return response_model

def get_all_patient_patient_guardian_by_guardianId(db: Session, UserId: int):
    patient_guardian_relationships =  db.query(PatientPatientGuardian).join(Patient).join(PatientGuardian).join(PatientGuardianRelationshipMapping).filter(PatientGuardian.guardianApplicationUserId == UserId).all()
    db_patient_guardian = PatientGuardianModel.from_orm(patient_guardian_relationships[0].patient_guardian)
    patients = []
    for row in patient_guardian_relationships:
        patient = row.patient
        relationship_name = row.relationship.relationshipName
        
        patient_with_relationship = PatientWithRelationshipModel(
            patient=PatientModel.from_orm(patient),  # Convert ORM patient to Pydantic model
            relationshipName=relationship_name
        )
        patients.append(patient_with_relationship)
    response_model = {"patient_guardian": db_patient_guardian, "patients": patients}
    return response_model


def get_patient_patient_guardian_by_guardianId_and_patientId(db: Session, guardianId: int, patientId: int):
    return db.query(PatientPatientGuardian).filter(PatientPatientGuardian.guardianId == guardianId).filter(PatientPatientGuardian.patientId == patientId).first()

def create_patient_patient_guardian(db: Session, patientPatientGuradian: PatientPatientGuardianCreate):
    db_patient_patient_guardian = PatientPatientGuardian(**patientPatientGuradian.model_dump())
    updated_data_dict = serialize_data(patientPatientGuradian.model_dump())
    db.add(db_patient_patient_guardian)
    db.commit()
    db.refresh(db_patient_patient_guardian)

    log_crud_action(
        action=ActionType.CREATE,
        user=SYSTEM_USER_ID,
        table="PatientPatientGuardian",
        entity_id=db_patient_patient_guardian.id,
        original_data=None,
        updated_data=updated_data_dict,
        user_full_name="None",
        message="Create patient patient_guardian"
    )
    return db_patient_patient_guardian

def update_patient_patient_guardian(db: Session, id: int, patientPatientGuradian: PatientPatientGuardianUpdate):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.id == id).first()
    if db_relationship:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_relationship.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in patientPatientGuradian.model_dump().items():
            setattr(db_relationship, key, value)

        db.commit()
        db.refresh(db_relationship)

        updated_data_dict = serialize_data(patientPatientGuradian.model_dump())
        log_crud_action(
            action=ActionType.UPDATE,
            user=SYSTEM_USER_ID,
            table="PatientPatientGuardian",
            entity_id=id,
            original_data=original_data_dict,
            updated_data=updated_data_dict,
            user_full_name="None",
            message="Update patient patient_guardian"
        )
    return db_relationship

def delete_patient_patient_guardian_by_guardianId(db: Session, guardianId: int):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.guardianId == guardianId).first()
    if db_relationship:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_relationship.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_relationship, "isDeleted", "1")
        db.commit()
        db.refresh(db_relationship)

        log_crud_action(
            action=ActionType.DELETE,
            user=SYSTEM_USER_ID,
            table="PatientPatientGuardian",
            entity_id=db_relationship.id,
            original_data=original_data_dict,
            updated_data=None,
            user_full_name="None",
            message="Delete patient patient_guardian"
        )
    return db_relationship

def delete_relationship(db: Session, id: int):
    db_relationship = db.query(PatientPatientGuardian).filter(PatientPatientGuardian.id == id).first()
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
            user=SYSTEM_USER_ID,
            table="PatientPatientGuardian",
            entity_id=db_relationship.id,
            original_data=original_data_dict,
            updated_data=None,
        )
    return db_relationship
