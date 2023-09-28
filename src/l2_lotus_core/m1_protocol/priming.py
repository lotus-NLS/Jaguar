from __future__ import annotations
from typing import Union
import platform, distro

from src.l2_lotus_core.m1_protocol.objective import Objective
from src.l2_lotus_core.m1_protocol.identity_definitions import *

# ----------------------------------------------------

class Directive:
    @classmethod
    def make_empty_directive(cls) -> Directive:
        return cls(objective=None)

    def __init__(self, objective : Union[None,Objective]):
        self.root_objective : Union[None, Objective] = objective

    def is_active(self):
        return not self.root_objective is None

    # ----------------------------------------------------

    def get_str(self) -> str:
        return self.get_objective_msg()+self.get_mode_message()


    def get_objective_msg(self) -> str:
        objective_msg = '## My current objectives ##\n'
        if not self.root_objective is None:
            objective_msg += f'My current objective is:\n' \
                             f'{self.root_objective}\n'
        else:
            objective_msg += f'I don\'t currently have any objectives to fulfill. All done for now :)'
        return objective_msg


    def get_mode_message(self) -> str:
        is_working = self.is_active()

        if is_working:
            mode_msg = 'Your are currently in work mode. Fulfill all objectives including root or cancel the root objective to get back to dialogue mode.'

        else:
            mode_msg = 'You are in dialgoue mode and can converse with the user'

        return mode_msg



class Identity:
    def __init__(self,core : str):
        self.core : str = core
        self.os_information : str = self.get_detailed_os_info()

    @staticmethod
    def get_detailed_os_info():
        system = f'{platform.system()}'
        detail = system

        try:
            if system == "Windows":
                detail += f" version {platform.release()}"
            elif system == "Darwin":
                mac_ver, _, _ = platform.mac_ver()
                detail += f" version {mac_ver}"
            elif system == "Linux":
                distro_name, distro_version = distro.id(), distro.version()
                detail += f" - {distro_name} version {distro_version}"
        except Exception as e:
            detail += f" (Error obtaining additional details: {e})"

        return detail

    def get_str(self) -> str:
        identity_msg = f'{self.core}\n'
        os_msg = f'You operate on the OS: {self.os_information}'

        return identity_msg+os_msg


class Priming:

    @classmethod
    def make_goto_priming(cls) -> Priming:
        identity = Identity(core=goto)
        return cls(identity)

    @classmethod
    def make_website_summarization_priming(cls) -> Priming:
        return cls(Identity(core=website_information_retriever))
    
    @classmethod
    def make_report_composition_priming(cls) -> Priming:
        return cls(Identity(core=report_composer))

    @classmethod
    def make_single_purpose_priming(cls, identity_desc : str) -> Priming:
        return cls(identity=Identity(core=identity_desc))

    def __init__(self,identity : Identity, directive : Directive = Directive.make_empty_directive()):
        self._identity : Identity = identity
        self._directive : Directive = directive

    def get_identity_str(self) -> str:
        return self._identity.get_str()



