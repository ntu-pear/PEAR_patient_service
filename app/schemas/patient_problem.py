from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


class PatientProblemBase(BaseModel):
    PatientID: int
    ProblemListID: int
    DateOfDiagnosis: Optional[date] = None
    ProblemRemarks: Optional[str] = None
    SourceOfInformation: Optional[str] = None


class PatientProblemCreate(PatientProblemBase):
    pass


class PatientProblemUpdate(BaseModel):
    PatientID: Optional[int] = None
    ProblemListID: Optional[int] = None
    DateOfDiagnosis: Optional[date] = None
    ProblemRemarks: Optional[str] = None
    SourceOfInformation: Optional[str] = None


class PatientProblem(PatientProblemBase):
    Id: int
    IsDeleted: str
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedByID: str
    ModifiedByID: str

    model_config = {"from_attributes": True}


class PatientProblemWithDetails(PatientProblem):
    ProblemName: Optional[str] = None

    model_config = {"from_attributes": True}