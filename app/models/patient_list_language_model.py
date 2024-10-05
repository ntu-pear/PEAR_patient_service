from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class PatientListLanguage(Base):
    __tablename__ = "PATIENT_LIST_LANGUAGE"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    isDeleted = Column(String(1), default='0', nullable=False)  # used to check if record is active or not, substitute isDeleted column

    createdDateTime = Column(DateTime, nullable=False, default=datetime.now)
    modifiedDateTime = Column(DateTime, nullable=False, default=datetime.now)

    value = Column(String(255))