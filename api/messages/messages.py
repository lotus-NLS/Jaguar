from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional

# ----------------------------------------------
# Classes

class LotusRequest(BaseModel):
    user_id: str = 'default_id'
    bool_content: Optional[bool] = None
    msg: str = Field(default_factory=list)
    img : Optional[str] = None


class TranscribeRequest(BaseModel):
    audio_content : Optional[str] = None

