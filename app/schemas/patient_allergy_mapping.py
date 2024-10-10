from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientAllergyBase(BaseModel):
    AllergyRemarks: Optional[str] = Field(None, example="Patient has severe reactions")
    Active: Optional[str] = Field(default="1", example="1")

class PatientAllergyCreate(PatientAllergyBase):
    PatientID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)

class PatientAllergyUpdate(PatientAllergyBase):
    PatientID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)

class PatientAllergy(PatientAllergyBase):
    Patient_AllergyID: int = Field(example=1)
    PatientID: int = Field(example=1)
    AllergyTypeValue: str = Field(example="Corn")
    AllergyReactionTypeValue: str = Field(example="Rashes")
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    createdById: int = Field(example=1)
    modifiedById: int = Field(example=1)
    class Config:
        from_attributes = True