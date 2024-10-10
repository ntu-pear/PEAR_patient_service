from pydantic import BaseModel
from datetime import datetime

class PatientMobility_MobilityListBase(BaseModel):
    patient_id: int
    mobilityListId: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int

class PatientMobility_MobilityListCreate(PatientMobility_MobilityListBase):
    pass

class PatientMobility_MobilityListUpdate(PatientMobility_MobilityListBase):
    pass

class PatientMobility_MobilityList(PatientMobility_MobilityListBase):
    id: int

    class Config:
        from_attributes = True
