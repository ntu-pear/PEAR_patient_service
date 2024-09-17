from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ListLanguageBase(BaseModel):
    isDeleted: str                                      
    createdDateTime: datetime                               
    modifiedDateTime: datetime  
    value: str                 

class ListLanguageCreate(ListLanguageBase):
    pass

class ListLanguageUpdate(ListLanguageBase):
    pass           

class ListLanguage(ListLanguageBase):
    id: int # INT -> int (primary key)

    class Config:
        orm_mode = True
