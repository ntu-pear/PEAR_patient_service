from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AllergyTypeBase(BaseModel):
    Value: str = Field(example="Corn")
    Active: Optional[str] = Field(default="1", example="1")

class AllergyTypeCreate(AllergyTypeBase):
    pass

class AllergyTypeUpdate(AllergyTypeBase):
    pass

class AllergyType(AllergyTypeBase):
    AllergyTypeID: int = Field(example=1)
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
