from __future__ import annotations
from typing import Union, Optional


# ---------------------------------------------------------

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


class Objective:

    @classmethod
    def make_root(cls, desc : str) -> Objective:
        return cls(desc=desc, identifier='0')

    def __init__(self, desc : str, identifier : str):
        self.desc: str = f'{desc}'
        self.identifier : str = identifier
        self.is_active : bool = True

        self.child_list : list[Objective] = []
        self.parent : Optional[Objective] = None

        ops_list = [self.mark_successful, self.abandon, self.make_subelement, self.retry]
        self.ops_dict = {funct.__name__ : funct for funct in ops_list}

    # ----------------------------------------------------
    # get

    @classmethod
    def get_action_names(cls) -> list[str]:
        temp_obj = cls(desc='',identifier='')
        return [action.__name__ for action in temp_obj.ops_dict.values()]


    def get_objective_by_id(self, objective_id : str) -> Optional[Objective]:
        total_dict = self.get_descendant_dict()
        total_dict[self.identifier] = self

        if not objective_id in total_dict:
            raise KeyError(f'There is no objective with ID {objective_id}')

        return total_dict[objective_id]


    def get_descendant_dict(self) -> dict[str, Objective]:
        desc_dict = {}

        for child in self.child_list:
            desc_dict[child.identifier] = child
            child_desc_dict = child.get_descendant_dict()
            desc_dict.update(child_desc_dict)

        return desc_dict


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[ ]' if self.is_active else '[x]'

        obj_string = (f'{space}desc: {self.desc}\n'
                     f'{space}ID: {self.identifier}\n'
                     f'{space}Is done?: {completion_str}\n')

        children_list = self.child_list
        if children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string

    # ----------------------------------------------------
    #

    def mark_successful(self):
        self.is_active = False


    def retry(self):
        pass


    def abandon(self):
        self.is_active = False

        if not self.parent is None:
            self.parent.child_list.remove(self)


    def make_subelement(self, desc : str):
        new_element = Objective(desc=desc, identifier=f'{self.identifier}{len(self.child_list)}')
        new_element.parent = self
        self.child_list.append(new_element)

        return new_element
