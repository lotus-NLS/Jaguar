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
    def make_root(cls, desc : str):
        root_obj = cls(desc)
        root_obj.descendant_dict = {}
        root_obj.root_objective = root_obj
        return root_obj

    def __init__(self, desc : str):
        self.desc: str = f'{desc}'
        self.is_complete : bool = False
        self._uuid = f'{uuid.uuid4()}'[:5]

        self.child_objective_list : list[Objective] = []
        self.parent : Optional[Objective] = None
        self.root_objective : Optional[Objective] = None

        self.descendant_dict : Optional[dict[str,Objective]] = None

        act_list = [self.edit, self.mark_complete, self.cancel, self.make_subelement]
        self.available_actions = {funct.__name__ : funct for funct in act_list}

    # ----------------------------------------------------
    # get

    def get_objective(self, objective_key : str) -> Optional[Objective]:
        if self.descendant_dict is None:
            return

        else:
            return self.descendant_dict.get(objective_key)

    def get_key(self) -> str:
        return self._uuid


    def get_is_done(self) -> bool:
        return self.is_complete


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[x]' if self.is_complete else '[ ]'

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


    def edit(self, new_name : str) -> None:
        self.desc = new_name


    def mark_complete(self) -> None:
        if len(self.child_objective_list) == 0:
            self.is_complete = True
        else:
            all_children_status = [child.is_complete for child in self.child_objective_list]
            all_children_done = all(all_children_status)
            if all_children_done:
                self.is_complete = True


    def cancel(self):
        if not self.parent is None:
            self.parent.child_objective_list.remove(self)
            del self.root_objective.descendant_dict[self.get_key()]


    def make_subelement(self, name : str):
        new_element = Objective(desc=name)
        new_element.parent = self
        new_element.root_objective = self.root_objective

        self.root_objective.descendant_dict[new_element.get_key()] = new_element
        self.child_objective_list.append(new_element)

        return new_element

