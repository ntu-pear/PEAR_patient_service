from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Any, Dict, Optional


class refUserConfigCreate(BaseModel):
    """Schema for creating user config """
    UserConfigId: int
    configBlob: Dict[str, Any]
    modifiedDate: datetime
    modifiedById: str


class refUserConfigUpdate(BaseModel):
    """Schema for updating user config"""
    UserConfigId: int
    configBlob: Dict[str, Any]
    modifiedDate: Optional[datetime] = None
    modifiedById: Optional[str] = None
