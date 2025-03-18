from pydantic import BaseModel
from datetime import datetime
from typing import List

class SocialHistorySensitiveBase(BaseModel):
    socialHistoryItem: str
    isSensitive: bool

class SocialHistorySensitiveCreate(SocialHistorySensitiveBase):
    pass

class SocialHistorySensitiveUpdate(SocialHistorySensitiveBase):
    pass


class SocialHistorySensitive(SocialHistorySensitiveBase):
    createdById: str
    modifiedById: str
    createdDate: datetime
    modifiedDate: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
        }