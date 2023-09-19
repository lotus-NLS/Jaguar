from __future__ import annotations
from typing import Union
import platform, distro

from src.l2_lotus_core.m1_protocol.agenda_entry import Objective,Task
from src.l2_lotus_core.m1_protocol.identity_definitions import *

# ----------------------------------------------------

# NOTE :This is currently in test mode because of disappointing performance with GPT 3.5
class Directive:
    @classmethod
    def make_empty_directive(cls) -> Directive:
        return cls(task=None,objective=None)

    def __init__(self,task : Union[None,Task], objective : Union[None,Task]):
        self.current_task : Union[None,Task] = task
        self.current_objective : Union[None, Objective] = objective

    def get_msg(self) -> str:
        objective_msg = '## My current objectives ##\n'
        if not self.current_objective is None:
            objective_msg += f'Your current objective is:\n' \
                            f'{self.current_objective}\n'
        else:
            # objective_msg += f'You do not currently have any objective to fulfill. All done for now :)'
            objective_msg += f'I have to obtain eggwhite!\n'

        task_msg = '## My current tasks ##\n'
        if not self.current_task is None:
            task_msg += f'In achieving this objective you are charged with the following task\n' \
                       f'{self.current_task}\n'
        else:
            # task_msg += f'I do not currently have any task to work on :)'
            task_msg += f'I must crack an egg!\n'

        return objective_msg+task_msg


class Identity:
    def __init__(self,core : str, principles : str):
        self.core : str = core
        self.principles : str = principles
        self.os_information : str = self.get_detailed_os_info()

    @staticmethod
    def get_detailed_os_info():
        system = platform.system()
        detail = system

        try:
            if system == "Windows":
                detail += f" version {platform.release()}"
            elif system == "Darwin":
                mac_ver, _, _ = platform.mac_ver()
                detail += f" version {mac_ver}"
            elif system == "Linux":
                distro_name, distro_version, _ = distro.id()
                detail += f" - {distro_name} version {distro_version}"
        except Exception as e:
            detail += f" (Error obtaining additional details: {e})"

        return detail

    def get_msg(self) -> str:
        core_msg = f'{self.core}\n'
        principles_msg = f'{self.principles}\n'
        os_msg = f'You operate on the OS: {self.os_information}'

        return core_msg+principles_msg+os_msg


class Priming:

    @classmethod
    def make_goto_priming(cls) -> Priming:
        identity = Identity(core=goto,principles='')
        return cls(identity)

    @classmethod
    def make_website_summarization_priming(cls) -> Priming:
        return cls(Identity(core=website_information_retriever, principles=''))
    
    @classmethod
    def make_report_composition_priming(cls) -> Priming:
        return cls(Identity(core=report_composer,principles=''))

    @classmethod
    def make_single_purpose_priming(cls, identity_desc : str) -> Priming:
        return cls(identity=Identity(core=identity_desc,principles=''))

    def __init__(self,identity : Identity, directive : Directive = Directive.make_empty_directive()):
        self._identity : Identity = identity
        self._directive : Directive = directive

    def get_identity_msg(self) -> str:
        return self._identity.get_msg()



