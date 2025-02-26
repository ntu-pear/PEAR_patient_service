from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientEducationListBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Primary or lower"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientEducationListTypeCreate(PatientEducationListBase):
    pass


class PatientEducationListTypeUpdate(PatientEducationListBase):
    pass


class PatientEducationListType(PatientEducationListBase):
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: int = Field(json_schema_extra={"example": 1})
    ModifiedById: int = Field(json_schema_extra={"example": 1})
    model_config = {"from_attributes": True}
