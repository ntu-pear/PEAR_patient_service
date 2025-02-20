from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AllergyTypeBase(BaseModel):
    Value: str = Field(json_schema_extra={"example": "Corn"})
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})


class AllergyTypeCreate(AllergyTypeBase):
    pass


class AllergyTypeUpdate(AllergyTypeBase):
    pass


class AllergyType(AllergyTypeBase):
    AllergyTypeID: int = Field(json_schema_extra={"example": 1})
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: str = Field(json_schema_extra={"example": "1"})
    ModifiedById: str = Field(json_schema_extra={"example": "1"})
    
    model_config = {"from_attributes": True}
