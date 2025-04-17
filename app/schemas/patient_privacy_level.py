from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.patient_privacy_level_model import PrivacyStatus

class PatientPrivacyLevelBase(BaseModel):
    accessLevelSensitive: Optional[PrivacyStatus] = None

class PatientPrivacyLevelCreate(PatientPrivacyLevelBase):
    active: Optional[bool] = None

class PatientPrivacyLevelUpdate(PatientPrivacyLevelBase):
    active: Optional[bool] = None

class PatientPrivacyLevel(PatientPrivacyLevelBase):
    patientId: int
    active: bool
    createdById: str
    modifiedById: str
    createdDate: datetime
    modifiedDate: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
        }