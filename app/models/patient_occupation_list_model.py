from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class PatientOccupationList(Base):
    __tablename__ = "PATIENT_OCCUPATION_LIST"

    Id = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(String(1), default='0', nullable=False) 
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    Value = Column(String(255))