from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPrescriptionBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    PrescriptionListId: int
    Dosage: str
    FrequencyPerDay: int
    Instruction: str
    StartDate: datetime
    EndDate: Optional[datetime] = None
    IsAfterMeal: Optional[str] = None
    PrescriptionRemarks: str
    Status: Optional[str] = None

class PatientPrescriptionCreate(PatientPrescriptionBase):
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: int
    UpdatedById: int

class PatientPrescriptionUpdate(PatientPrescriptionBase):
    UpdatedDateTime: datetime
    UpdatedById: int

class PatientPrescription(PatientPrescriptionBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: int
    UpdatedById: int

    model_config = {"from_attributes": True}
