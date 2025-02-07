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
    CreatedById: str
    UpdatedById: str

class PatientPrescriptionUpdate(PatientPrescriptionBase):
    UpdatedDateTime: datetime
    UpdatedById: str

class PatientPrescription(PatientPrescriptionBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str
    UpdatedById: str

    model_config = {"from_attributes": True}
