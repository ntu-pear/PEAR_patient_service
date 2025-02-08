from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientDietListBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Diabetic"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientDietListCreate(PatientDietListBase):
    pass


class PatientDietListUpdate(PatientDietListBase):
    pass


class PatientDietListType(PatientDietListBase):
    List_DietID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}
