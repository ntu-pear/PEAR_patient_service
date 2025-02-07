from pydantic import BaseModel, Field
from datetime import datetime

class PatientGuardianRelationshipMappingBase(BaseModel):
    IsDeleted: str
    RelationshipName: str


class PatientGuardianRelationshipMappingCreate(PatientGuardianRelationshipMappingBase):
    CreatedDate: datetime = Field(default_factory=datetime.now)


class PatientGuardianRelationshipMappingUpdate(PatientGuardianRelationshipMappingBase):
    ModifiedDate: datetime = Field(default_factory=datetime.now)

class PatientGuardianRelationshipMapping(PatientGuardianRelationshipMappingBase):
    id: int
    CreatedDate: datetime
    ModifiedDate: datetime
    CreatedById: int
    ModifiedById: int
    