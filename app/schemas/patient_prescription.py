from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPrescriptionBase(BaseModel):
    active: Optional[str] = '1'
    patientId: int
    # prescriptionListId: int
    dosage: str
    frequencyPerDay: int
    instruction: str
    startDate: datetime
    endDate: Optional[datetime] = None
    afterMeal: Optional[str] = None
    prescriptionRemarks: str
    status: str = None

class PatientPrescriptionCreate(PatientPrescriptionBase):
    createdDateTime: datetime
    modifiedDateTime: datetime
    createdById: int
    modifiedById: int

class PatientPrescriptionUpdate(PatientPrescriptionBase):
    modifiedDateTime: datetime
    modifiedById: int

class PatientPrescription(PatientPrescriptionBase):
    id: int
    createdDateTime: datetime
    modifiedDateTime: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True
