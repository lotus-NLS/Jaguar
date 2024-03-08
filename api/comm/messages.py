from typing import Optional
from dataclasses import dataclass

from ..language.entry import Entry
from .._serialization import Dillable

# ----------------------------------------------
# Classes

@dataclass
class APIMessage(Dillable):
    def __init__(self, entry : Optional[Entry] = None, choice : Optional[bool] = None):
        self.user_id : str = 'default_id'
        self.entry_str : Optional[Entry] = entry
        self.bool_content : Optional[bool] = choice
