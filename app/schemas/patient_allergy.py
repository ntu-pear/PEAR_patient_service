from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientAllergyBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    allergyListId: int
    allergyReactionListId: int
    allergyRemarks: Optional[str] = None

class PatientAllergyCreate(PatientAllergyBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientAllergyUpdate(PatientAllergyBase):
    modifiedDate: datetime
    modifiedById: int

class PatientAllergy(PatientAllergyBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        orm_mode: True
