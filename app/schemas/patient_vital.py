from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional

class PatientVitalBase(BaseModel):
    IsDeleted: Optional[str] = '0'
    PatientId: int
    IsAfterMeal: str
    Temperature: float
    SystolicBP: int
    DiastolicBP: int
    HeartRate: int
    SpO2: int
    BloodSugarLevel: int
    Height: float
    Weight: float
    VitalRemarks: Optional[str] = None

class PatientVitalCreate(PatientVitalBase):
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

class PatientVitalUpdate(PatientVitalBase):
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    UpdatedDateTime: Optional[datetime] = None

class PatientVitalDelete(BaseModel):
    Id: int

class PatientVital(PatientVitalBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})

    model_config = {"from_attributes": True}
