from sqlalchemy.orm import Session
from ..models.patient_doctor_note_model import PatientDoctorNote
from ..schemas.patient_doctor_note import PatientDoctorNoteCreate, PatientDoctorNoteUpdate

def get_doctor_notes(db: Session, patient_id: int):
    return db.query(PatientDoctorNote).filter(PatientDoctorNote.patient_id == patient_id).all()

def create_doctor_note(db: Session, doctor_note: PatientDoctorNoteCreate):
    db_doctor_note = PatientDoctorNote(**doctor_note.dict())
    db.add(db_doctor_note)
    db.commit()
    db.refresh(db_doctor_note)
    return db_doctor_note

def update_doctor_note(db: Session, note_id: int, doctor_note: PatientDoctorNoteUpdate):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()
    if db_doctor_note:
        for key, value in doctor_note.dict().items():
            setattr(db_doctor_note, key, value)
        db.commit()
        db.refresh(db_doctor_note)
    return db_doctor_note

def delete_doctor_note(db: Session, note_id: int, doctor_note: PatientDoctorNoteUpdate):
    db_doctor_note = db.query(PatientDoctorNote).filter(PatientDoctorNote.id == note_id).first()
    if db_doctor_note:
        for key, value in doctor_note.dict().items():
            setattr(db_doctor_note, key, value)
        db.commit()
        db.refresh(db_doctor_note)
    return db_doctor_note
