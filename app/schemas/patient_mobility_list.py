from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PatientMobilityListBase(BaseModel):
    mobilityListId: int
    IsDeleted: bool
    createdDate: datetime
    modifiedDate: datetime
    value: str

class PatientMobilityListCreate(PatientMobilityListBase):
    pass

class PatientMobilityListUpdate(PatientMobilityListBase):
    pass

class PatientMobilityList(PatientMobilityListBase):
    id: int

    class Config:
        orm_mode = True
