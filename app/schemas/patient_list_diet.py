from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientDietListBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Diabetic"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientDietListTypeCreate(PatientDietListBase):
    pass


class PatientDietListTypeUpdate(PatientDietListBase):
    pass


class PatientDietListType(PatientDietListBase):
    Id: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: int = Field(json_schema_extra={"example": 1})
    ModifiedById: int = Field(json_schema_extra={"example": 1})
    model_config = {"from_attributes": True}
