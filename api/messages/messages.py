from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional

# ----------------------------------------------
# Classes

class LotusRequest(BaseModel):
    user_id: str = 'default_id'
    bool_content: Optional[bool] = None
    msg: str = ''
    img : Optional[str] = None


class TranscribeRequest(BaseModel):
    wav_bytes : bytes = None

