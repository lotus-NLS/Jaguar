from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.l2_models import InfOptions, CallOptions
from engine.l2_models.context import Entry


# ------------------------------------------------------------------------

@dataclass
class Step:
    memory: Optional[Entry] = None
    notice: Optional[Entry] = None
    required_tool: Optional[str] = None

    @classmethod
    def make_default(cls, msg : str):
        return cls(memory=Entry.user(msg=msg))

    def get_options(self) -> InfOptions:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.required_tool)
        return InfOptions(call_options=call_options)



if __name__ == "__main__":
    pass