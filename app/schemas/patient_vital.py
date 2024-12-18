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
    ModifiedById: int

class PatientVitalUpdate(PatientVitalBase):
    ModifiedById: int
    ModifiedDateTime: Optional[datetime] = None

class PatientVitalDelete(BaseModel):
    Id: int

class PatientVital(PatientVitalBase):
    Id: int
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: int
    ModifiedById: int

    class Config:
        from_attributes = True
