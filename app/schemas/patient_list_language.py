from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientListLanguageBase(BaseModel):
    isDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})                                      
    value: str                            

class PatientListLanguageCreate(PatientListLanguageBase):
    pass

class PatientListLanguageUpdate(PatientListLanguageBase):
    pass
class PatientListLanguage(PatientListLanguageBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    model_config = {"from_attributes": True}