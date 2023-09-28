from __future__ import annotations
from typing import Optional
import uuid


# The objectives should be navigable on their own, e.g. without any module to support them
# That necessitates the following attributes in each objective:
# -> List of child nodes
# -> Parent node
# -> root objective

# Objective needs to implement
# Add subobjective, Edit, mark complete, cancel

# ----------------------------------------------------


class Objective:

    @classmethod
    def make_root(cls, desc : str) -> Objective:
        return cls(desc=desc)

    def __init__(self, desc : str):
        self.desc: str = f'{desc}'
        self._uuid : str = f'{uuid.uuid4()}'[:5]
        self.is_active : bool = True

        self.child_objective_list : list[Objective] = []
        self.parent : Optional[Objective] = None

        act_list = [self.edit_desc, self.mark_complete, self.cancel, self.make_subelement]
        self.available_actions = {funct.__name__ : funct for funct in act_list}

    # ----------------------------------------------------
    # get

    def get_objective(self, objective_key : str) -> Optional[Objective]:
        total_dict = self.get_descendant_dict()
        total_dict[self._uuid] = self

        if not objective_key in total_dict:
            raise KeyError(f'There is no objective with ID {objective_key}')

        return total_dict[objective_key]


    def get_descendant_dict(self) -> dict[str, Objective]:
        desc_dict = {}

        for child in self.child_objective_list:
            desc_dict[child._uuid] = child
            child_desc_dict = child.get_descendant_dict()
            desc_dict.update(child_desc_dict)

        return desc_dict


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[ ]' if self.is_active else '[x]'

        obj_string = (f'{space}desc: {self.desc}\n'
                     f'{space}ID: {self._uuid}\n'
                     f'{space}Is done?: {completion_str}\n')

        children_list = self.child_objective_list
        if children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string

    # ----------------------------------------------------
    # set

    def edit_desc(self, desc : str) -> None:
        self.desc = desc

    def mark_complete(self) -> None:
        self.is_active = False


    def cancel(self):
        self.is_active = False

        if not self.parent is None:
            self.parent.child_objective_list.remove(self)


    def make_subelement(self, desc : str):
        new_element = Objective(desc=desc)
        new_element.parent = self
        self.child_objective_list.append(new_element)

        return new_element

