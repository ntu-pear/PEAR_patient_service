from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientMobility(Base):
    __tablename__ = "PATIENT_MOBILITY"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(Boolean, default=False, nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patient_id = Column(Integer, ForeignKey('PATIENT.id'), nullable=False)  # Ensure this field exists
    mobilityListId = Column(Integer, ForeignKey('PATIENT_LIST.id'))  # Changed to Integer
    status = Column(String(255))

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="mobility_records")
    mobility_list = relationship("PatientList", back_populates="mobility_records")
