from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientAssignedDementiaMapping(Base):
    __tablename__ = "PATIENT_ASSIGNED_DEMENTIA_MAPPING"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    IsDeleted = Column(String(1), default="0", nullable=False)  # boolean 1 or 0
    PatientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    DementiaTypeListId = Column(Integer, ForeignKey('PATIENT_ASSIGNED_DEMENTIA_LIST.DementiaTypeListId'))  # Changed to Integer

    CreatedDate = Column(DateTime, nullable=False, default=DateTime)
    ModifiedDate = Column(DateTime, nullable=False, default=DateTime)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String
    
    patient = relationship("Patient", back_populates="assigned_dementias")

    dementia_type = relationship(
        "PatientAssignedDementiaList",
        backref="dementia_assignments",
        primaryjoin="PatientAssignedDementiaMapping.DementiaTypeListId == PatientAssignedDementiaList.DementiaTypeListId",
    )
