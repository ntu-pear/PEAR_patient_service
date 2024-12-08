from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientVitalBase(BaseModel):
    active: Optional[str] = '1'
    patientId: int
    afterMeal: str
    temperature: float
    systolicBP: int
    diastolicBP: int
    heartRate: int
    spO2: int
    bloodSugarLevel: int
    height: float
    weight: float
    vitalRemarks: Optional[str] = None

class PatientVitalCreate(PatientVitalBase):
    createdById: int
    modifiedById: int

class PatientVitalUpdate(PatientVitalBase):
    modifiedById: int
    modifiedDateTime: Optional[datetime] = None

class PatientVitalDelete(BaseModel):
    id: int

class PatientVital(PatientVitalBase):
    id: int
    createdDateTime: datetime
    modifiedDateTime: datetime
    createdById: int
    modifiedById: int

    class Config:
        from_attributes = True
