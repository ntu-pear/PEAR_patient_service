from datetime import datetime
from sqlalchemy.orm import Session
from ..models.patient_doctor_note_model import PatientDoctorNote
from ..schemas.patient_doctor_note import PatientDoctorNoteCreate, PatientDoctorNoteUpdate

def get_doctor_notes_by_patient(db: Session, patient_id: int):
    return db.query(PatientDoctorNote).filter(PatientDoctorNote.patientId == patient_id).all()

def get_doctor_note_by_id(db: Session, note_id: int):
    return db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()

def create_doctor_note(db: Session, doctor_note: PatientDoctorNoteCreate):
    db_doctor_note = PatientDoctorNote(**doctor_note.model_dump())
    if db_doctor_note:
        db_doctor_note.createdDate = datetime.now()
        db_doctor_note.modifiedDate = datetime.now()
        db.add(db_doctor_note)
        db.commit()
        db.refresh(db_doctor_note)
    return db_doctor_note

def update_doctor_note(db: Session, note_id: int, doctor_note: PatientDoctorNoteUpdate):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()
    if db_doctor_note:
        for key, value in doctor_note.model_dump().items():
            setattr(db_doctor_note, key, value)
        db_doctor_note.modifiedDate = datetime.now()
        db.commit()
        db.refresh(db_doctor_note)
    return db_doctor_note

def delete_doctor_note(db: Session, note_id: int):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()
    if db_doctor_note:
        setattr(db_doctor_note, 'isDeleted', '1')
        db.commit()
        db.refresh(db_doctor_note)
    return db_doctor_note
