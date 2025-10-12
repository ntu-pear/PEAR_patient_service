from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PatientPrescriptionListBase(BaseModel):
    IsDeleted: bool
    Value: str

class PatientPrescriptionListCreate(PatientPrescriptionListBase):
    CreatedDateTime: datetime
    UpdatedDateTime: datetime

class PatientPrescriptionListUpdate(PatientPrescriptionListBase):
    UpdatedDateTime: datetime

class PatientPrescriptionList(PatientPrescriptionListBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime

    model_config = {"from_attributes": True}
