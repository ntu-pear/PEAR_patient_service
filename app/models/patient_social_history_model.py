from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientSocialHistory(Base):
    __tablename__ = "PATIENT_SOCIAL_HISTORY"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    sexuallyActive = Column(String(1))
    secondHandSmoker = Column(String(1))
    alcoholUse = Column(String(1))
    caffeineUse = Column(String(1))
    tobaccoUse = Column(String(1))
    drugUse = Column(String(1))
    exercise = Column(String(1))

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="social_histories")
    # list_mappings = relationship("PatientSocialHistoryListMapping", back_populates="social_history")
