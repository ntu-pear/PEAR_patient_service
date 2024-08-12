from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_doctor_note_crud as crud_doctor_note
from ..schemas.patient_doctor_note import (
    PatientDoctorNote,
    PatientDoctorNoteCreate,
    PatientDoctorNoteUpdate
)

router = APIRouter()

@router.get("/DoctorNote", response_model=list[PatientDoctorNote])
def get_doctor_notes(patient_id: int, db: Session = Depends(get_db)):
    return crud_doctor_note.get_doctor_notes(db, patient_id)

@router.post("/DoctorNote/add", response_model=PatientDoctorNote)
def create_doctor_note(doctor_note: PatientDoctorNoteCreate, db: Session = Depends(get_db)):
    return crud_doctor_note.create_doctor_note(db, doctor_note)

@router.put("/DoctorNote/update", response_model=PatientDoctorNote)
def update_doctor_note(note_id: int, doctor_note: PatientDoctorNoteUpdate, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.update_doctor_note(db, note_id, doctor_note)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    return db_doctor_note

@router.delete("/DoctorNote/delete", response_model=PatientDoctorNote)
def delete_doctor_note(note_id: int, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.delete_doctor_note(db, note_id)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    return db_doctor_note
