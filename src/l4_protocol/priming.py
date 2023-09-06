from __future__ import annotations
from typing import Union
from src.l4_protocol.agenda_entry import Objective,Task

# ----------------------------------------------------

# NOTE :This is currently in test mode because of disappointing performance
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
    @classmethod
    def make_identity_from_file(cls, fpath : str) -> Identity:
        try:
            with open(fpath) as identity_file:
                identity_desc = identity_file.read()
            return Identity(core=identity_desc,principles='')
        except Exception as e:
            print(f'[Error]: An error has occured while trying to set agent identity: {e}')
            raise ValueError

    def __init__(self,core : str, principles : str):
        self.core : str = core
        self.principles : str = principles

    def get_msg(self) -> str:
        core_msg = f'{self.core}\n'
        principles_msg = f'{self.principles}\n'

        return core_msg+principles_msg


class Priming:
    def get_identity_msg(self) -> str:
        return self._identity.get_msg()

    @classmethod
    def make_lotus_priming(cls) -> Priming:
        identity = Identity.make_identity_from_file(fpath='../l4_protocol/IdentityDefinitions/lotus_agent')
        directives = Directive.make_empty_directive()
        return cls(identity,directives)

    @classmethod
    def make_from_fpath(cls,fpath):
        identity = Identity.make_identity_from_file(fpath=fpath)
        directives = Directive.make_empty_directive()
        return cls(identity, directives)

    @classmethod
    def make_single_purpose_priming(cls, identity_desc : str) -> Priming:
        identity = Identity(core=identity_desc,principles='')
        directives = Directive.make_empty_directive()
        return cls(identity,directives)

    def __init__(self,identity : Identity, directive : Directive):
        self._identity : Identity = identity
        self._directive : Directive = directive