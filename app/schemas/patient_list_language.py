from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientListLanguageBase(BaseModel):
    IsDeleted: Optional[str] = Field(default="0", json_schema_extra={"example": "0"})                                      
    Value: str                            

class PatientListLanguageCreate(PatientListLanguageBase):
    pass

class PatientListLanguageUpdate(PatientListLanguageBase):
    pass
class PatientListLanguage(PatientListLanguageBase):
    id: int
    CreatedDate: datetime
    ModifiedDate: datetime
    model_config = {"from_attributes": True}