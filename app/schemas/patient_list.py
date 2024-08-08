from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PatientListBase(BaseModel):
    active: Optional[str] = 'Y'
    type: str
    value: str
    listOrder: Optional[int] = None

class PatientListCreate(PatientListBase):
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifyById: int

class PatientListUpdate(PatientListBase):
    modifiedDate: datetime
    modifyById: int

class PatientList(PatientListBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifyById: int

    class Config:
        orm_mode: True
