from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPrescriptionBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    prescriptionListId: int
    dosage: Optional[str] = None
    frequencyPerDay: Optional[int] = None
    instruction: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    afterMeal: Optional[str] = None
    prescriptionRemarks: Optional[str] = None
    status: Optional[str] = None

class PatientPrescriptionCreate(PatientPrescriptionBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientPrescriptionUpdate(PatientPrescriptionBase):
    modifiedDate: datetime
    modifiedById: int

class PatientPrescription(PatientPrescriptionBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True
