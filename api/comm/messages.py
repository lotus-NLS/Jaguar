from typing import Optional
from dataclasses import dataclass

from hollarek.templates import Dillable
from ..language.entry import Entry

# ----------------------------------------------
# Classes

@dataclass
class APIMessage(Dillable):
    def __init__(self, entry : Optional[Entry] = None, choice : Optional[bool] = None):
        self.user_id : str = 'default_id'
        self.entry_str : Optional[Entry] = entry
        self.bool_content : Optional[bool] = choice
