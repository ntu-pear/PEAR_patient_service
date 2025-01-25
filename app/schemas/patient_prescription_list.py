from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPrescriptionListBase(BaseModel):
    IsDeleted: bool
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    Value: str

class PatientPrescriptionListCreate(PatientPrescriptionListBase):
    pass

class PatientPrescriptionListUpdate(PatientPrescriptionListBase):
    pass

class PatientPrescriptionList(PatientPrescriptionListBase):
    Id: int

    model_config = {"from_attributes": True}
