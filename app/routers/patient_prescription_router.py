from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import patient_prescription_crud as crud_prescription
from ..schemas.patient_prescription import PatientPrescription, PatientPrescriptionCreate, PatientPrescriptionUpdate
from ..schemas.response import SingleResponse, PaginatedResponse

router = APIRouter()

@router.get("/Prescription", response_model=PaginatedResponse[PatientPrescription])
def get_prescriptions(pageNo: int = 0, pageSize: int = 100, db: Session = Depends(get_db)):
    db_prescriptions, totalRecords, totalPages =  crud_prescription.get_prescriptions(db, pageNo=pageNo, pageSize=pageSize)
    patient_prescriptions = [PatientPrescription.model_validate(patient_prescription) for patient_prescription in db_prescriptions]
    return PaginatedResponse(data=patient_prescriptions, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)

@router.get("/Prescription/PatientPrescription", response_model=PaginatedResponse[PatientPrescription])
def get_patient_prescriptions(patient_id: int, pageNo: int = 0, pageSize: int = 100, db: Session = Depends(get_db)):
    db_prescriptions, totalRecords, totalPages =  crud_prescription.get_patient_prescriptions(db,patient_id, pageNo=pageNo, pageSize=pageSize)
    patient_prescriptions = [PatientPrescription.model_validate(patient_prescription) for patient_prescription in db_prescriptions]
    return PaginatedResponse(data=patient_prescriptions, pageNo=pageNo, pageSize=pageSize, totalRecords= totalRecords, totalPages=totalPages)


# TODO
@router.get("/Prescription/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.get_prescription(db, prescription_id)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)


@router.post("/Prescription/add", response_model=SingleResponse[PatientPrescription])
def create_prescription(prescription: PatientPrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription =  crud_prescription.create_prescription(db, prescription)
    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)

@router.put("/Prescription/update/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def update_prescription(prescription_id: int, prescription: PatientPrescriptionUpdate, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.update_prescription(db, prescription_id, prescription)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)

@router.put("/Prescription/delete/{prescription_id}", response_model=SingleResponse[PatientPrescription])
def delete_prescription(prescription_id: int, prescription: PatientPrescriptionUpdate, db: Session = Depends(get_db)):
    db_prescription = crud_prescription.delete_prescription(db, prescription_id, prescription)
    if not db_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    patient_prescription = PatientPrescription.model_validate(db_prescription)
    return SingleResponse(data=patient_prescription)
