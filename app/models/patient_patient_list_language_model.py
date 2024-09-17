from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Patient_PatientListLanguage(Base):
    __tablename__ = "PATIENT_PATIENT_LIST_LANGUAGE"

    id = Column(Integer, primary_key=True, index=True)  # Changed to Integer
    patientId = Column(Integer, ForeignKey('PATIENT.id'), nullable=False)  # Changed to Integer
    listLanguageId = Column(Integer, ForeignKey('PATIENT_LIST_LANGUAGE.id'), nullable=False)

    # createdDate = Column(DateTime, nullable=False, default=DateTime)
    # modifiedDate = Column(DateTime, nullable=False, default=DateTime)
    # createdById = Column(Integer, nullable=False)
    # modifiedById = Column(Integer, nullable=False)