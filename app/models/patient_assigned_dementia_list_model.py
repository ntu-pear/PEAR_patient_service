from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class PatientAssignedDementiaList(Base):
    __tablename__ = "PATIENT_ASSIGNED_DEMENTIA_LIST"

    DementiaTypeListId = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(String(1), default="0", nullable=False)  # boolean 1 or 0

    Value = Column(String, nullable=False)
    CreatedById = Column(Integer, nullable=False)  # Add this field
    ModifiedById = Column(Integer, nullable=False)  # Add this field
    CreatedDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)