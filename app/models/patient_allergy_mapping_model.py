from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class PatientAllergy(Base):
    __tablename__ = "PATIENT_ALLERGY_MAPPING"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default="Y", nullable=False)
    patientId = Column(Integer, ForeignKey("PATIENT.id"))
    allergyRemarks = Column(String(255))
    createdDate = Column(DateTime, nullable=False, default=datetime.now)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)

    patient = relationship("Patient", back_populates="allergies")
