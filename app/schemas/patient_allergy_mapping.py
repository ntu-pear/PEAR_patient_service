from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PatientAllergyBase(BaseModel):
    AllergyRemarks: Optional[str] = Field(None, example="Patient has severe reactions")
    IsDeleted: Optional[str] = Field(default="0", example="0")


class PatientAllergyCreate(PatientAllergyBase):
    PatientID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)


class PatientAllergyCreateResp(PatientAllergyBase):
    PatientID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: int = Field(example=1)
    ModifiedById: int = Field(example=1)


class PatientAllergyUpdateReq(PatientAllergyBase):
    Patient_AllergyID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)


class PatientAllergyUpdateResp(PatientAllergyBase):
    PatientID: int = Field(example=1)
    Patient_AllergyID: int = Field(example=1)
    AllergyTypeID: int = Field(example=3)
    AllergyReactionTypeID: int = Field(example=1)
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: int = Field(example=1)
    ModifiedById: int = Field(example=1)


class PatientAllergy(PatientAllergyBase):
    Patient_AllergyID: int = Field(example=1)
    PatientID: int = Field(example=1)
    AllergyTypeValue: str = Field(example="Corn")
    AllergyReactionTypeValue: str = Field(example="Rashes")
    CreatedDateTime: datetime = Field(default_factory=datetime.now)
    UpdatedDateTime: datetime = Field(default_factory=datetime.now)
    CreatedById: int = Field(example=1)
    ModifiedById: int = Field(example=1)

    model_config = {"from_attributes": True}
