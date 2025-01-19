from pydantic import BaseModel
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
    CreatedById: int
    UpdatedById: int

class PatientVitalUpdate(PatientVitalBase):
    UpdatedById: int
    UpdatedDateTime: Optional[datetime] = None

class PatientVitalDelete(BaseModel):
    Id: int

class PatientVital(PatientVitalBase):
    Id: int
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: int
    UpdatedById: int

    model_config = {"from_attributes": True}
