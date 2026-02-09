from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientPhotoListAlbum(Base):
    __tablename__ = "PATIENT_PHOTO_LIST_ALBUM"

    AlbumCategoryListID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IsDeleted = Column(Integer, default=0, nullable=False)
    Value = Column(String, nullable=False)

    CreatedDateTime = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedDateTime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    CreatedById = Column(String, nullable=False)
    ModifiedById = Column(String, nullable=False)

    # Relationship with PatientPhoto
    photos = relationship(
        "PatientPhoto",
        back_populates="album_category"
    )