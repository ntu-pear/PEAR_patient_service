from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Patient_PatientListLanguageBase(BaseModel):
    patientId: int                                      
    listLanguageId: int                               

class Patient_PatientListLanguageCreate(Patient_PatientListLanguageBase):
    pass

class Patient_PatientListLanguageUpdate(Patient_PatientListLanguageBase):
    pass           

class Patient_PatientListLanguage(Patient_PatientListLanguageBase):
    id: int # INT -> int (primary key)

    class Config:
        orm_mode = True
