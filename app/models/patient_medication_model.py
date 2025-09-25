from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientMedication(Base):
    __tablename__ = "PATIENT_MEDICATION"

    Id = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(String(1), default='0', nullable=False)  # Fixed: default should be '0' for active records
    PatientId = Column(Integer, ForeignKey('PATIENT.id'))
    PrescriptionListId = Column(Integer, ForeignKey('PATIENT_PRESCRIPTION_LIST.Id'))
    AdministerTime = Column(String(255), nullable=False)
    Dosage = Column(String(255), nullable=False)
    Instruction = Column(String(255), nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime)
    PrescriptionRemarks = Column(String(255), nullable=False)

    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedById = Column(String, nullable=False)
    ModifiedById = Column(String, nullable=False)

    # Fixed relationships - create separate relationship names
    patient = relationship("Patient", back_populates="medications")
    prescription_list = relationship("PatientPrescriptionList", back_populates="medications")
