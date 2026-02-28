from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey



class RefUserConfig(Base):
    __tablename__ = "REF_USERCONFIG"

    UserConfigID = Column(Integer, primary_key=True, index=True)
    configBlob = Column(String, nullable=False)
    modifiedDate = Column(DateTime, nullable=False)
    modifiedById = Column(String, nullable=False)
