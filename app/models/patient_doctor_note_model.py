from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientDoctorNote(Base):
    __tablename__ = "PATIENT_DOCTORNOTE"

    id = Column(Integer, primary_key=True, index=True) 
    patientId = Column(Integer, ForeignKey('PATIENT.id')) 
    doctorId = Column(Integer)  
    doctorRemarks = Column(String(255))
    isDeleted = Column(String(1), default="0", nullable=False)

    createdDate = Column(DateTime, nullable=False, default=DateTime)
    modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String

    patient = relationship("Patient", back_populates="doctor_notes")
