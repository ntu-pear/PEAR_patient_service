from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientProblemListBase(BaseModel):
    ProblemName: str


class PatientProblemListCreate(PatientProblemListBase):
    pass


class PatientProblemListUpdate(BaseModel):
    ProblemName: Optional[str] = None


class PatientProblemList(PatientProblemListBase):
    Id: int
    IsDeleted: str
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedByID: str
    ModifiedByID: str

    model_config = {"from_attributes": True}