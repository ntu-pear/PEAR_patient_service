# from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base

# class PatientSocialHistoryListMapping(Base):
#     __tablename__ = "PATIENT_SOCIAL_HISTORY_LIST_MAPPING"

#     id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
#     # socialHistoryId = Column(Integer, ForeignKey('PATIENT_SOCIAL_HISTORY.id'))  # Changed to Integer
#     # listId = Column(Integer, ForeignKey('PATIENT_LIST.id'))  # Changed to Integer

#     # social_history = relationship("PatientSocialHistory", back_populates="list_mappings")
#     # list_entry = relationship("PatientList", back_populates="social_history_mappings")
