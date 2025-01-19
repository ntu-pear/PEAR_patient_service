from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientSocialHistoryBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    patientId: int
    sexuallyActive: Optional[str] = None
    secondHandSmoker: Optional[str] = None
    alcoholUse: Optional[str] = None
    caffeineUse: Optional[str] = None
    tobaccoUse: Optional[str] = None
    drugUse: Optional[str] = None
    exercise: Optional[str] = None

class PatientSocialHistoryCreate(PatientSocialHistoryBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientSocialHistoryUpdate(PatientSocialHistoryBase):
    modifiedDate: datetime
    modifiedById: int

class PatientSocialHistory(PatientSocialHistoryBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    model_config = {"from_attributes": True}
