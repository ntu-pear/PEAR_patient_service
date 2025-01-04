from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientPrescriptionListBase(BaseModel):
    active: bool
    createdDateTime: datetime
    modifiedDateTime: datetime
    value: str

class PatientPrescriptionListCreate(PatientPrescriptionListBase):
    pass

class PatientPrescriptionListUpdate(PatientPrescriptionListBase):
    pass

class PatientPrescriptionList(PatientPrescriptionListBase):
    id: int

    model_config = {"from_attributes": True}
