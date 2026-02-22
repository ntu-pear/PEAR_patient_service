from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientProblem(Base):
    __tablename__ = "PATIENT_PROBLEM"

    Id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(Integer, ForeignKey('PATIENT.id'), nullable=False, index=True)
    ProblemListID = Column(Integer, ForeignKey('PATIENT_PROBLEM_LIST.Id'), nullable=False, index=True)
    DateOfDiagnosis = Column(Date, nullable=True)
    ProblemRemarks = Column(String(500), nullable=True)
    SourceOfInformation = Column(String(255), nullable=True)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(450), nullable=False)
    ModifiedByID = Column(String(450), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="problems")
    problem_list = relationship("PatientProblemList", back_populates="problems")