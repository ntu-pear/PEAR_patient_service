from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientVital(Base):
    __tablename__ = "PATIENT_VITAL"

    Id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    IsDeleted = Column(String(1), default='0', nullable=False)
    PatientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    IsAfterMeal = Column(String(1), nullable=False)
    Temperature = Column(Float(5), nullable=False)
    SystolicBP = Column(Integer, nullable=False)
    DiastolicBP = Column(Integer, nullable=False)
    HeartRate = Column(Integer, nullable=False)
    SpO2 = Column(Integer, nullable=False)
    BloodSugarLevel = Column(Integer, nullable=False)
    Height = Column(Float(5), nullable=False)
    Weight = Column(Float(5), nullable=False)
    VitalRemarks = Column(String(255))

    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(Integer, nullable=False)  # Changed to Integer
    ModifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="vitals")
