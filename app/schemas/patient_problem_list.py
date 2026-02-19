from datetime import datetime
from pydantic import BaseModel, Field


class PatientProblemListBase(BaseModel):
    ProblemName: str = Field(min_length=1)


class PatientProblemListCreate(PatientProblemListBase):
    pass


class PatientProblemListUpdate(BaseModel):
    ProblemName: str = Field(min_length=1)


class PatientProblemList(PatientProblemListBase):
    Id: int
    IsDeleted: str
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedByID: str
    ModifiedByID: str

    model_config = {"from_attributes": True}