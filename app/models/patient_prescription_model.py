from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.patient_prescription_list_model import PatientPrescriptionList

class PatientPrescription(Base):
    __tablename__ = "PATIENT_PRESCRIPTION"

    Id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    IsDeleted = Column(String(1), default='1', nullable=False)  # used to check if record is active or not, substitute isDeleted column
    PatientId = Column(Integer, ForeignKey('PATIENT.id'))  # Changed to Integer
    PrescriptionListId = Column(Integer, ForeignKey('PATIENT_PRESCRIPTION_LIST.Id'))  # Changed to Integer
    Dosage = Column(String(255), nullable=False)
    FrequencyPerDay = Column(BigInteger, nullable=False)
    Instruction = Column(String(255), nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime)
    IsAfterMeal = Column(String(1))
    PrescriptionRemarks = Column(String(255), nullable=False)
    Status = Column(String(255), nullable=False)  # used in place of ischronic

    CreatedDateTime = Column(DateTime, nullable=False, default=DateTime)
    UpdatedDateTime = Column(DateTime, nullable=False, default=DateTime)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String

    patient = relationship("Patient", back_populates="prescriptions")
    prescription_list = relationship("PatientPrescriptionList", back_populates="prescriptions")
