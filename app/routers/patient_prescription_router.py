from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_prescription_crud as crud_prescription
from ..schemas import patient_prescription as schemas_prescription

router = APIRouter()

@router.get("/Prescription", response_model=list[schemas_prescription.PatientPrescription])
def get_prescriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_prescription.get_prescriptions(db, skip=skip, limit=limit)

@router.get("/Prescription/PatientPrescription", response_model=list[schemas_prescription.PatientPrescription])
def get_patient_prescriptions(patient_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_prescription.get_patient_prescriptions(db, patient_id, skip=skip, limit=limit)

# TODO
@router.get("/Prescription/{prescription_id}", response_model=schemas_prescription.PatientPrescription)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@router.post("/Prescription/add", response_model=schemas_prescription.PatientPrescription)
def create_prescription(prescription: schemas_prescription.PatientPrescriptionCreate, db: Session = Depends(get_db)):
    return crud_prescription.create_prescription(db, prescription)

@router.put("/Prescription/update/{prescription_id}", response_model=schemas_prescription.PatientPrescription)
def update_prescription(prescription_id: int, prescription: schemas_prescription.PatientPrescriptionUpdate, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.update_prescription(db, prescription_id, prescription)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription

@router.put("/Prescription/delete/{prescription_id}", response_model=schemas_prescription.PatientPrescription)
def delete_prescription(prescription_id: int, prescription: schemas_prescription.PatientPrescriptionUpdate, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.delete_prescription(db, prescription_id, prescription)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return db_prescription
