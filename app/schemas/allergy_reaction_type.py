from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AllergyReactionTypeBase(BaseModel):
    Value: str = Field(example="Rashes")
    Active: Optional[str] = Field(default="1", example="1")

class AllergyReactionTypeCreate(AllergyReactionTypeBase):
    pass

class AllergyReactionTypeUpdate(AllergyReactionTypeBase):
    pass

class AllergyReactionType(AllergyReactionTypeBase):
    AllergyReactionTypeID: int = Field(example=1)
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    createdById: int = Field(example=1)
    modifiedById: int = Field(example=1)
    class Config:
        from_attributes = True