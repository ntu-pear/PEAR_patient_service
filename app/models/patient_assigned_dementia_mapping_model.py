from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientAssignedDementiaMapping(Base):
    __tablename__ = "PATIENT_ASSIGNED_DEMENTIA_MAPPING"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    dementiaTypeListId = Column(Integer, ForeignKey('PATIENT_ASSIGNED_DEMENTIA_LIST.dementiaTypeListId'))  # Changed to Integer

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer
    
    patient = relationship("Patient", back_populates="assigned_dementias")

    dementia_type = relationship(
        "PatientAssignedDementiaList",
        backref="dementia_assignments",
        primaryjoin="PatientAssignedDementiaMapping.dementiaTypeListId == PatientAssignedDementiaList.dementiaTypeListId",
    )
