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
from ..schemas.response import SingleResponse, PaginatedResponse

router = APIRouter()

@router.get("/DoctorNote/GetDoctorNotesByPatient", response_model=PaginatedResponse[PatientDoctorNote])
def get_doctor_notes_by_patient_id(patient_id: int, pageNo: int = 0, pageSize: int = 10, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, patient_id):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    db_notes, totalRecords, totalPages = crud_doctor_note.get_doctor_notes_by_patient(db=db, patient_id = patient_id, pageNo=pageNo, pageSize=pageSize)
    notes = [PatientDoctorNote.model_validate(note) for note in db_notes]
    return PaginatedResponse(data=notes, pageNo= pageNo, totalRecords= totalRecords, totalPages = totalPages)

@router.get("/DoctorNote", response_model=SingleResponse[PatientDoctorNote])
def get_doctor_note(note_id: int, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.get_doctor_note_by_id(db, note_id)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Invalid note id")
    doctor_note = PatientDoctorNote.model_validate(db_doctor_note)
    return SingleResponse(data= doctor_note)

@router.post("/DoctorNote/add", response_model=SingleResponse[PatientDoctorNote])
def create_doctor_note(doctor_note: PatientDoctorNoteCreate, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, doctor_note.patientId):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    db_doctor_note = crud_doctor_note.create_doctor_note(db, doctor_note)
    doctor_note = PatientDoctorNote.model_validate(db_doctor_note)
    return SingleResponse(data= doctor_note)

@router.put("/DoctorNote/update", response_model=SingleResponse[PatientDoctorNote])
def update_doctor_note(doctor_note: PatientDoctorNoteUpdate, note_id: int, db: Session = Depends(get_db)):
    if not crud_patient.get_patient(db, doctor_note.patientId):
        raise HTTPException(status_code=404, detail="Patient does not exist")
    db_doctor_note = crud_doctor_note.update_doctor_note(db, note_id, doctor_note)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    
    doctor_note = PatientDoctorNote.model_validate(db_doctor_note)
    return SingleResponse(data= doctor_note)

@router.delete("/DoctorNote/delete", response_model=SingleResponse[PatientDoctorNote])
def delete_doctor_note(note_id: int, db: Session = Depends(get_db)):
    db_doctor_note = crud_doctor_note.delete_doctor_note(db, note_id)
    if not db_doctor_note:
        raise HTTPException(status_code=404, detail="Doctor note not found")
    doctor_note = PatientDoctorNote.model_validate(db_doctor_note)
    return SingleResponse(data= doctor_note)
