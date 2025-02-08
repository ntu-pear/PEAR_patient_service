from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientOccupationListBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Accountant"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientOccupationListCreate(PatientOccupationListBase):
    pass


class PatientOccupationListUpdate(PatientOccupationListBase):
    pass


class PatientOccupationListType(PatientOccupationListBase):
    List_DietID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}
