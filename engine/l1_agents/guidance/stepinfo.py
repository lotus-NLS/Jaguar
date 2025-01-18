from __future__ import annotations

from typing import Optional

from engine.l2_models import Options, CallOptions
from engine.l2_models.context import Entry


# ------------------------------------------------------------------------

class StepInfo:
    def __init__(self, memory : Optional[Entry] = None, notice :  Optional[Entry] = None, required_tool_name : Optional[str] = None):
        self.memory_update : Entry = memory
        self.notice : Entry = notice
        self.required_tool : Optional[str] = required_tool_name

    @classmethod
    def make_default(cls, msg : str):
        return cls(memory=Entry.user(msg=msg))

    def get_options(self) -> Options:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.required_tool)
        return Options(call_options=call_options)



if __name__ == "__main__":
    pass