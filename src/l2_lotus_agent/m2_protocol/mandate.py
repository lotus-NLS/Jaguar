from __future__ import annotations

from typing import Union, Optional

from src.l2_lotus_agent import Objective


class Mandate:
    @classmethod
    def make_empty(cls) -> Mandate:
        return cls(objective=None)

    def __init__(self, objective : Union[None,Objective]):
        self.root_objective : Union[None, Objective] = objective

    def is_active(self):
        return not self.root_objective is None

    # ----------------------------------------------------

    def get_msg(self) -> Optional[str]:
        if not self.is_active():
            return None

        if self.root_objective is None:
            return None

        objective_msg = (f'## Internal monologue: My current mandate, which I am working to finish is:'
                         f'\n{self.root_objective}\n')
        mode_msg = ('I am currently in work mode and cannot speak to the user.'
                    'The root objective must be completed or canceled via UPDATE_MANDATE to get back to dialogue mode and converse with the user.'
                    'Once an objective is completed, I will mark it as complete using UPDATE_MANDATE')

        return objective_msg + mode_msg
