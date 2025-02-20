from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.l2_models import InfOptions, CallOptions
from engine.l2_models.context import Entry
from engine.l3_aos.workspaces.taskws import Mandate


# ------------------------------------------------------------------------

@dataclass
class Step:
    mode : str = 'work'
    task : Optional[Mandate] = None
    required_tool: Optional[str] = None

    def __post_init__(self):
        valid_mode_options = ['work', 'converse']
        if not self.mode in valid_mode_options:
            raise ValueError(f'Invalid mode: {self.mode}; Mode options are {valid_mode_options}')

    def get_options(self) -> InfOptions:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.required_tool)
        return InfOptions(call_options=call_options)



if __name__ == "__main__":
    pass