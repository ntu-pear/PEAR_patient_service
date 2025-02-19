from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PatientPhoto(Base):
    __tablename__ = "PATIENT_PHOTO"

    PatientPhotoID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    IsDeleted = Column(Integer, default=0, nullable=False)
    PhotoPath = Column(String, nullable=False)
    PhotoDetails = Column(String, nullable=True)
    AlbumCategoryListID = Column(Integer, ForeignKey("PATIENT_PHOTO_LIST_ALBUM.AlbumCategoryListID", ondelete="CASCADE"), nullable=False)
    PatientID = Column(Integer, ForeignKey('PATIENT.id', ondelete="CASCADE"), nullable=False)

    CreatedDateTime = Column(DateTime, default=datetime.utcnow, nullable=False)
    UpdatedDateTime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    CreatedById = Column(String, nullable=False)  # Changed to String
    ModifiedById = Column(String, nullable=False)  # Changed to String

    # Relationship with Patient
    patient = relationship("Patient", back_populates="photos")

    # Fix: Ensure album_category refers to PatientPhotoList, not PatientList
    album_category = relationship(
        "PatientPhotoList",
        back_populates="photos",
        foreign_keys=[AlbumCategoryListID]
    )
