from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientLiveWithListBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Alone"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientLiveWithListTypeCreate(PatientLiveWithListBase):
    pass


class PatientLiveWithListTypeUpdate(PatientLiveWithListBase):
    pass


class PatientLiveWithListType(PatientLiveWithListBase):
    ID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}
