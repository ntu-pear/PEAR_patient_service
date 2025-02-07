from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientAssignedDementiaBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    DementiaTypeListId: int

class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str
    ModifiedById: str

class PatientAssignedDementiaUpdate(PatientAssignedDementiaBase):
    ModifiedDate: datetime
    ModifiedById: int

class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: str
    ModifiedById: str

    model_config = {"from_attributes": True}