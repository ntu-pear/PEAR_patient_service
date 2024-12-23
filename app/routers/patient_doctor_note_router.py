from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import (
    patient_doctor_note_crud as crud_doctor_note,
    patient_crud as crud_patient
    )
from ..schemas.patient_doctor_note import (
    PatientDoctorNote,
    PatientDoctorNoteCreate,
    PatientDoctorNoteUpdate
)

router = APIRouter()

@router.get("/DoctorNote/GetDoctorNotesByPatient", response_model=list[PatientDoctorNote])
def get_doctor_notes_by_patient_id(patient_id: int, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, patient_id):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    return crud_doctor_note.get_doctor_notes_by_patient(db, patient_id)

@router.get("/DoctorNote", response_model=PatientDoctorNote)
def get_doctor_note(note_id: int, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.get_doctor_note_by_id(db, note_id)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Invalid note id")
    return db_doctor_note

@router.post("/DoctorNote/add", response_model=PatientDoctorNote)
def create_doctor_note(doctor_note: PatientDoctorNoteCreate, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, doctor_note.patientId):
        raise HTTPException(status_code=404, detail="Patient does not exist")
     
    return crud_doctor_note.create_doctor_note(db, doctor_note)

@router.put("/DoctorNote/update", response_model=PatientDoctorNote)
def update_doctor_note(doctor_note: PatientDoctorNoteUpdate, note_id: int, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, doctor_note.patientId):
        raise HTTPException(status_code=404, detail="Patient does not exist")
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
