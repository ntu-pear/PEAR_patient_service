from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class AllergyType(Base):
    __tablename__ = "ALLERGY_TYPE"

    AllergyTypeID = Column(Integer, primary_key=True, index=True)
    Value = Column(String(255), nullable=False)  
    IsDeleted = Column(String(0), default="0", nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String