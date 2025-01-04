from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientMobilityBase(BaseModel):
    active: int
    patient_id: int
    mobilityListId: int
    status: Optional[str] = None

class PatientMobilityCreate(PatientMobilityBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientMobilityUpdate(PatientMobilityBase):
    modifiedDate: datetime
    modifiedById: int

class PatientMobility(PatientMobilityBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

    model_config = {"from_attributes": True}
