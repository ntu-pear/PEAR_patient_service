from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_doctor_note_crud as crud_doctor_note
from ..schemas import patient_doctor_note as schemas_doctor_note

router = APIRouter()

@router.get("/DoctorNote", response_model=list[schemas_doctor_note.DoctorNote])
def get_doctor_notes(patient_id: int, db: Session = Depends(get_db)):
    return crud_doctor_note.get_doctor_notes(db, patient_id)

@router.post("/DoctorNote/add", response_model=schemas_doctor_note.DoctorNote)
def create_doctor_note(doctor_note: schemas_doctor_note.DoctorNoteCreate, db: Session = Depends(get_db)):
    return crud_doctor_note.create_doctor_note(db, doctor_note)

@router.put("/DoctorNote/update", response_model=schemas_doctor_note.DoctorNote)
def update_doctor_note(note_id: int, doctor_note: schemas_doctor_note.DoctorNoteUpdate, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.update_doctor_note(db, note_id, doctor_note)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    return db_doctor_note

@router.put("/DoctorNote/delete", response_model=schemas_doctor_note.DoctorNote)
def delete_doctor_note(note_id: int, doctor_note: schemas_doctor_note.DoctorNoteUpdate, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.delete_doctor_note(db, note_id, doctor_note)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    return db_doctor_note
