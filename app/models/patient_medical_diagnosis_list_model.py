from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class PatientMedicalDiagnosisList(Base):
    __tablename__ = "PATIENT_MEDICAL_DIAGNOSIS_LIST"

    Id = Column(Integer, primary_key=True, index=True)
    DiagnosisName = Column(String(255), nullable=False)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(255), nullable=False)
    ModifiedByID = Column(String(255), nullable=False)