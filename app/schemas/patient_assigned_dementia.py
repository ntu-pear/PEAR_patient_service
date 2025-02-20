from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class PatientAssignedDementiaBase(BaseModel):
    active: Optional[str] = 'Y'
    patientId: int
    dementiaTypeListId: int

class PatientAssignedDementiaCreate(PatientAssignedDementiaBase):
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientAssignedDementiaUpdate(PatientAssignedDementiaBase):
    modifiedDate: datetime
    modifiedById: int

class PatientAssignedDementia(PatientAssignedDementiaBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    model_config = {"from_attributes": True}
