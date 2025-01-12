from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientMobilityListBase(BaseModel):
    MobilityListId: int
    IsDeleted: int
    CreatedDateTime: datetime
    ModifiedDateTime: datetime
    CreatedById: int
    ModifiedById: int
    Value: str

class PatientMobilityListCreate(PatientMobilityListBase):
    pass

class PatientMobilityListUpdate(PatientMobilityListBase):
    pass

class PatientMobilityList(PatientMobilityListBase):
    pass

    class Config:
        from_attributes = True
