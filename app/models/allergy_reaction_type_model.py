from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class AllergyReactionType(Base):
    __tablename__ = "ALLERGY_REACTION_TYPE"

    AllergyReactionTypeID = Column(Integer, primary_key=True, index=True)
    Value = Column(String(255), nullable=False)  
    Active = Column(String(1), default="1", nullable=False)
    CreatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
    UpdatedDateTime = Column(DateTime, nullable=False, default=datetime.now)
