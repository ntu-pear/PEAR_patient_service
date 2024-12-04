from pydantic import BaseModel, Field
from datetime import datetime

class PatientGuardianRelationshipMappingBase(BaseModel):
    isDeleted: str
    relationshipName: str


class PatientGuardianRelationshipMappingCreate(PatientGuardianRelationshipMappingBase):
    createdDate: datetime = Field(default_factory=datetime.now)


class PatientGuardianRelationshipMappingUpdate(PatientGuardianRelationshipMappingBase):
    modifiedDate: datetime = Field(default_factory=datetime.now)

class PatientGuardianRelationshipMapping(PatientGuardianRelationshipMappingBase):
    id: int
    createdDate: datetime
    modifiedDate: datetime
    createdById: int
    modifiedById: int
    