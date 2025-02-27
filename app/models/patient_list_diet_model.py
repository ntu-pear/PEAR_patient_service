from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class PatientDietList(Base):
    __tablename__ = "PATIENT_LIST_DIET"

    Id = Column(Integer, primary_key=True, index=True)
    IsDeleted = Column(String(1), default='0', nullable=False) 
    Value = Column(String(255))
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(String, nullable=False, default=1)
    ModifiedById = Column(String, nullable=False, default=1)