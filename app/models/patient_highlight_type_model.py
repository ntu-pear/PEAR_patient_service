from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class HighlightType(Base):
    __tablename__ = "PATIENT_HIGHLIGHT_TYPE"

    HighlightTypeID = Column(Integer, primary_key=True, index=True)
    Value = Column(String(255), nullable=False)  
    IsDeleted = Column(String(0), default="0", nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(Integer, nullable=False, default=1)  
    ModifiedById = Column(Integer, nullable=False, default=1)
