from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime
from app.database import Base

class PatientHighlight(Base):
    __tablename__ = "PATIENT_HIGHLIGHT"

    Id = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(String(1), default="0", nullable=False)
    PatientId = Column(Integer, ForeignKey("PATIENT.id"), nullable=False)
    Type = Column(String(255), nullable=False)
    HighlightJSON = Column(String(255), nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime, nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.now)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(Integer, nullable=False, default=1)
    ModifiedById = Column(Integer, nullable=False, default=1)
    
    patient = relationship("Patient", back_populates="highlights")