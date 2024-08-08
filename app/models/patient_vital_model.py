from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientVital(Base):
    __tablename__ = "PATIENT_VITAL"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    active = Column(String(1), default='Y', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    patientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    afterMeal = Column(String(1))
    temperature = Column(Float(5))
    systolicBP = Column(Integer)
    diastolicBP = Column(Integer)
    heartRate = Column(Integer)
    spO2 = Column(Integer)
    bloodSugarLevel = Column(Integer)
    height = Column(Float(5))
    weight = Column(Float(5))

    createdDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)  # Changed to Integer
    modifiedById = Column(Integer, nullable=False)  # Changed to Integer

    patient = relationship("Patient", back_populates="vitals")
