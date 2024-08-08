from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientMobilityBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    mobilityListId: int
    status: Optional[str] = None

class PatientMobilityCreate(PatientMobilityBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientMobilityUpdate(PatientMobilityBase):
    modifiedDate: datetime
    modifiedById: int

class PatientMobility(PatientMobilityBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        orm_mode: True
