from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientMedicationAdministrationMark(BaseModel):
    MedicationId: int
    ScheduledTime: str = Field(
        min_length=1, max_length=5,
        description="One of the course's AdministerTime slots, e.g. 0800 (08:00 also accepted)",
        json_schema_extra={"example": "0800"},
    )
    AdministerDate: Optional[date] = Field(
        default=None,
        description="The dose's day in Singapore time. Defaults to the SGT date of ActualAdministerTime.",
    )
    ActualAdministerTime: Optional[datetime] = Field(
        default=None,
        description="When the dose was given. Without a timezone it is read as UTC. Defaults to now.",
    )


class PatientMedicationAdministration(BaseModel):
    Id: int
    MedicationId: int
    PatientId: int
    AdministerDate: date
    ScheduledTime: str
    ActualAdministerTime: datetime
    AdministeredById: str
    IsDeleted: str
    CreatedDateTime: datetime
    UpdatedDateTime: datetime
    CreatedById: str
    ModifiedById: str

    model_config = {"from_attributes": True}