from pydantic import BaseModel,Field
from datetime import datetime
from typing import List, Optional

class PatientListBase(BaseModel):
    active: Optional[str] = 'Y'
    type: str
    value: str
    listOrder: Optional[int] = None

class PatientListCreate(PatientListBase):
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientListUpdate(PatientListBase):
    modifiedDate: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientList(PatientListBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
