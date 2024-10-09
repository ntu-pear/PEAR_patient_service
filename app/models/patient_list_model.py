from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class PatientList(Base):
    __tablename__ = "PATIENT_LIST"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(String(1), default='Y', nullable=False)
    type = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    listOrder = Column(Integer)

    createdDate = Column(DateTime, nullable=False)
    modifiedDate = Column(DateTime, nullable=False, default=datetime.datetime.now)
    createdById = Column(Integer, nullable=False)
    modifiedById = Column(Integer, nullable=False)

    #guardians = relationship("PatientGuardian", back_populates="patient_list")
    # allergies = relationship("PatientAllergy", back_populates="allergy_list", foreign_keys="[PatientAllergy.allergyListId]")
    # allergy_reactions = relationship("PatientAllergy", back_populates="allergy_reaction_list", foreign_keys="[PatientAllergy.allergyReactionListId]")
    photos = relationship("PatientPhoto", back_populates="album_category")
    dementia_assignments = relationship("PatientAssignedDementia", back_populates="dementia_type")
    mobility_records = relationship("PatientMobility", back_populates="mobility_list")
    prescriptions = relationship("PatientPrescription", back_populates="prescription_list")
    # social_history_mappings = relationship("PatientSocialHistoryListMapping", back_populates="list_entry")