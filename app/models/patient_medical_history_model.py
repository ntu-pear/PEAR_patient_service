from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.patient_medical_diagnosis_list_model import PatientMedicalDiagnosisList


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
    
    _diagnosis = relationship(
        PatientMedicalDiagnosisList,
        foreign_keys=[MedicalDiagnosisID],
        lazy="joined"
    )
    
    @property
    def diagnosis_name(self) -> Optional[str]:
        """Return the diagnosis name if it's not deleted"""
        if self._diagnosis and self._diagnosis.IsDeleted == "0":
            return self._diagnosis.DiagnosisName
        return None