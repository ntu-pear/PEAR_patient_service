from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PatientPrescriptionListBase(BaseModel):
    Value: str = Field(..., example="Paracetamol")
    IsDeleted: Optional[bool] = Field(default=False, example=False)

class PatientPrescriptionListCreate(PatientPrescriptionListBase):
    CreatedDateTime: Optional[datetime] = None
    UpdatedDateTime: Optional[datetime] = None

class PatientPrescriptionListUpdate(PatientPrescriptionListBase):
    UpdatedDateTime: Optional[datetime] = None

class PatientPrescriptionList(PatientPrescriptionListBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime

    model_config = {"from_attributes": True}
