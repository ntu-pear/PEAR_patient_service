from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.patient_doctor_note_model import PatientDoctorNote
from ..schemas.patient_doctor_note import PatientDoctorNoteCreate, PatientDoctorNoteUpdate
from ..logger.logger_utils import log_crud_action, ActionType, serialize_data
import json
import math

def get_doctor_notes_by_patient(db: Session, patient_id: int, pageNo: int = 0, pageSize: int = 10):
    offset = pageNo * pageSize
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.patientId == patient_id, PatientDoctorNote.isDeleted == '0').order_by(PatientDoctorNote.patientId.desc()).offset(offset).limit(pageSize).all()
    totalRecords = db.query(func.count()).select_from(PatientDoctorNote).filter(PatientDoctorNote.patientId == patient_id,PatientDoctorNote.isDeleted == '0').scalar()
    totalPages = math.ceil(totalRecords/pageSize)
    return db_doctor_note, totalRecords, totalPages

def get_doctor_note_by_id(db: Session, note_id: int):
    return db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()

def create_doctor_note(db: Session, doctor_note: PatientDoctorNoteCreate, user_id: str, user_full_name: str):
    db_doctor_note = PatientDoctorNote(**doctor_note.model_dump())
    if db_doctor_note:
        db_doctor_note.createdDate = datetime.now()
        db_doctor_note.modifiedDate = datetime.now()
        db.add(db_doctor_note)
        db.commit()
        db.refresh(db_doctor_note)

        updated_data_dict = serialize_data(doctor_note.model_dump())

        log_crud_action(
            action=ActionType.CREATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Created doctor note",
            table="Doctor Note",
            entity_id=None,
            original_data=None,
            updated_data=updated_data_dict
        )
    return db_doctor_note

def update_doctor_note(db: Session, note_id: int, doctor_note: PatientDoctorNoteUpdate, user_id: str, user_full_name: str):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()

    if db_doctor_note:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_doctor_note.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        for key, value in doctor_note.model_dump().items():
            setattr(db_doctor_note, key, value)

        db_doctor_note.modifiedDate = datetime.now()
        db.commit()
        db.refresh(db_doctor_note)

        updated_data_dict = serialize_data(doctor_note.model_dump())

        log_crud_action(
            action=ActionType.UPDATE,
            user=user_id,
            user_full_name=user_full_name,
            message="Updated doctor note",
            table="Doctor Note",
            entity_id=note_id,
            original_data=original_data_dict,
            updated_data=updated_data_dict
        )

    return db_doctor_note

def delete_doctor_note(db: Session, note_id: int, user_id: str, user_full_name: str):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()
    if db_doctor_note:
        try: 
            original_data_dict = {
                k: serialize_data(v) for k, v in db_doctor_note.__dict__.items() if not k.startswith("_")
            }
        except Exception as e:
            original_data_dict = "{}"

        setattr(db_doctor_note, 'isDeleted', '1')
        db.commit()
        db.refresh(db_doctor_note)

        log_crud_action(
            action=ActionType.DELETE,
            user=user_id,
            user_full_name=user_full_name,
            message="Deleted doctor note",
            table="Doctor Note",
            entity_id=note_id,
            original_data=original_data_dict,
            updated_data=None
        )
    return db_doctor_note
