from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientDementiaStageList(Base):
    __tablename__ = "PATIENT_DEMENTIA_STAGE_LIST"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    DementiaStage = Column(String(50), nullable=False)
    IsDeleted = Column(String(1), default="0", nullable=False)
    CreatedDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    ModifiedDate = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedById = Column(String, nullable=False)
    ModifiedById = Column(String, nullable=False)