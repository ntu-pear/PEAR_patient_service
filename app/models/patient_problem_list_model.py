from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class PatientProblemList(Base):
    __tablename__ = "PATIENT_PROBLEM_LIST"

    Id = Column(Integer, primary_key=True, index=True)
    ProblemName = Column(String(255), nullable=False)
    IsDeleted = Column(String(1), default='0', nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedByID = Column(String(450), nullable=False)
    ModifiedByID = Column(String(450), nullable=False)

    # Relationship to patient problems
    problems = relationship(
        "PatientProblem",
        back_populates="problem_list"
    )