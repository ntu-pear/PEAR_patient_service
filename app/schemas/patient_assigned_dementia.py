from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientAssignedDementiaBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    dementiaTypeListId: int

class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientAssignedDementiaUpdate(PatientAssignedDementiaBase):
    modifiedDate: datetime
    modifiedById: int

class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    class Config:
        orm_mode: True
