from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HighlightBase(BaseModel):
    patientId: int
    description: str
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int


class HighlightCreate(HighlightBase):
    pass


class HighlightUpdate(BaseModel):
    description: Optional[str] = None
    modifiedDate: datetime
    modifiedById: int


class Highlight(HighlightBase):
    id: int

    model_config = {"from_attributes": True}
