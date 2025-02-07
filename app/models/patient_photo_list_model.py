from app.models.patient_photo_model import PatientPhoto
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientPhotoList(Base):
    __tablename__ = "PATIENT_PHOTO_LIST_ALBUM"

    AlbumCategoryListID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IsDeleted = Column(Integer, default=0, nullable=False)
    Value = Column(String, nullable=False)

    CreatedDateTime = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedDateTime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    CreatedById = Column(Integer, nullable=False)
    ModifiedById = Column(Integer, nullable=False)

    # Corrected Relationship
    photos = relationship(
        "PatientPhoto",
        back_populates="album_category",
        foreign_keys=[PatientPhoto.AlbumCategoryListID]
    )
