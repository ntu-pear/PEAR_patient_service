from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class PatientAssignedDementiaList(Base):
    __tablename__ = "PATIENT_ASSIGNED_DEMENTIA_LIST"

    dementiaTypeListId = Column(Integer, primary_key=True, index=True)
    isDeleted = Column(String(1), default="0", nullable=False)  # boolean 1 or 0
    createdDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    value = Column(String, nullable=False)
