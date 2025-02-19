from pydantic import BaseModel,Field
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
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientSocialHistoryUpdate(PatientSocialHistoryBase):
    modifiedDate: datetime
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientSocialHistory(PatientSocialHistoryBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
