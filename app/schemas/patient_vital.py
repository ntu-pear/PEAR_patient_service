from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientVitalBase(BaseModel):
    active: Optional[str] = '1'
    patientId: int
    afterMeal: Optional[str] = None
    temperature: Optional[float] = None
    systolicBP: Optional[int] = None
    diastolicBP: Optional[int] = None
    heartRate: Optional[int] = None
    spO2: Optional[int] = None
    bloodSugarLevel: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
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
        orm_mode: True
