from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from app.database import Base

class SocialHistorySensitiveMapping(Base):
    __tablename__ = "SOCIAL_HISTORY_SENSITIVE_MAPPING"

    id = Column(Integer, primary_key=True, index=True) 
    socialHistoryItem = Column(String(255), nullable=False, unique=True)
    isSensitive = Column(Boolean, default=True, nullable=False)

    createdDate = Column(DateTime, server_default=func.now(), nullable=False)
    modifiedDate = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    createdById = Column(String, nullable=False)
    modifiedById = Column(String, nullable=False)