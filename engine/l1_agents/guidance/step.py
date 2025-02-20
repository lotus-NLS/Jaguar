from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from engine.l1_agents.guidance.workflowy import Mandate
from engine.l2_models import InfOptions, CallOptions


# ------------------------------------------------------------------------

class StepModes(Enum):
    WORK = 'work'
    CONVERSE = 'converse'

@dataclass
class Step:
    mode : StepModes = StepModes.WORK
    mandate : Optional[Mandate] = None
    required_tool: Optional[str] = None

    def __post_init__(self):
        valid_mode_options = [StepModes.WORK]
        if not self.mode in valid_mode_options:
            raise ValueError(f'Invalid mode: {self.mode}; Mode options are {valid_mode_options}')

    @classmethod
    def converse(cls):
        return cls(mode=StepModes.CONVERSE)

    @classmethod
    def work(cls, mandate : Mandate):
        return cls(mode=StepModes.WORK, mandate=mandate)

    def get_options(self) -> InfOptions:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.required_tool)
        return InfOptions(call_options=call_options)


if __name__ == "__main__":
    pass