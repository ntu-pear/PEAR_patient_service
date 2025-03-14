from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HighlightTypeBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "newPrescription"})
    IsDeleted: str = Field(default="0", json_schema_extra={"example": "0"})

class HighlightTypeCreate(HighlightTypeBase):
    pass

class HighlightTypeUpdate(HighlightTypeBase):
    pass

class HighlightType(HighlightTypeBase):
    HighlightTypeID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    model_config = {"from_attributes": True}
