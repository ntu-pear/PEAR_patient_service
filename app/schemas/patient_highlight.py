from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientHighlightBase(BaseModel):
    PatientId: int = Field(json_schema_extra={"example": 1})
    Type: str = Field(json_schema_extra={"example": "Allergy"})
    HighlightJSON: str = Field(..., json_schema_extra={"example": '{"id":1,"value":"Shellfish"}'})
    StartDate: datetime = Field(..., json_schema_extra={"example": "2024-03-03T00:00:00"})
    EndDate: datetime = Field(..., json_schema_extra={"example": "2024-03-06T00:00:00"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class PatientHighlightCreate(PatientHighlightBase):
    pass

class PatientHighlightUpdate(PatientHighlightBase):
    pass

class PatientHighlight(PatientHighlightBase):
    Id: int = Field(..., json_schema_extra={"example": 1})
    CreatedDate: datetime = Field(..., json_schema_extra={"example": "2025-01-04T23:13:59.107"})
    ModifiedDate: datetime = Field(..., json_schema_extra={"example": "2025-01-04T23:13:59.107"})
    CreatedById: int = Field(..., json_schema_extra={"example": 1})
    ModifiedById: int = Field(..., json_schema_extra={"example": 1})

    model_config = {"from_attributes": True}
