from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientHighlightBase(BaseModel):
    PatientId: int = Field(..., example=1)
    Type: str = Field(..., example="Allergy")
    HighlightJSON: str = Field(..., example='{"id":1,"value":"Shellfish"}')
    StartDate: datetime = Field(..., example="2024-03-03T00:00:00")
    EndDate: datetime = Field(..., example="2024-03-06T00:00:00")
    IsDeleted: Optional[str] = Field(default="0", example="0")

class PatientHighlightCreate(PatientHighlightBase):
    pass

class PatientHighlightUpdate(PatientHighlightBase):
    pass

class PatientHighlight(PatientHighlightBase):
    Id: int = Field(..., example=1)
    CreatedDate: datetime = Field(..., example="2025-01-04T23:13:59.107")
    ModifiedDate: datetime = Field(..., example="2025-01-04T23:13:59.107")
    CreatedById: int = Field(..., example=1)
    ModifiedById: int = Field(..., example=1)


    model_config = {"from_attributes": True}
