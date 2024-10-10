from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class AllergyType(Base):
    __tablename__ = "ALLERGY_TYPE"

    AllergyTypeID = Column(Integer, primary_key=True, index=True)
    Value = Column(String(255), nullable=False)  
    Active = Column(String(1), default="1", nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    createdById = Column(Integer, nullable=False, default=1)  
    modifiedById = Column(Integer, nullable=False, default=1)