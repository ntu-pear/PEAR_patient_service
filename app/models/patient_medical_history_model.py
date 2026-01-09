from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientMedicalHistory(Base):
    __tablename__ = "PATIENT_MEDICAL_HISTORY"

    Id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey('PATIENT.id'), nullable=False)
    MedicalDiagnosisID = Column(Integer, ForeignKey('PATIENT_MEDICAL_DIAGNOSIS_LIST.Id'), nullable=False)
    DateOfDiagnosis = Column(Date, nullable=True)
    Remarks = Column(String(500), nullable=True)
    SourceOfInformation = Column(String(255), nullable=True)
    IsDeleted = Column(String(1), default="0", nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(255), nullable=False)
    ModifiedByID = Column(String(255), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="medical_histories")
    diagnosis = relationship("PatientMedicalDiagnosisList")