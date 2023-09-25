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
    def make_root(cls, name : str):
        return cls(name)

    def __init__(self, name : str ):
        self.desc: str = f'{name}'
        self.is_complete : bool = False

        self._uuid = f'{uuid.uuid4()}'[:5]
        self.child_objective_list : list[Objective] = []

        self.root_objective : Optional[Objective] = None

        # self.desc: str = f'Instructions: {instruction_text}'
        # self.actions = [self.edit_name, self.mark_complete, self.add_subelement]

    def is_done(self) -> bool:
        return self.is_complete

    def edit(self, new_name : str) -> None:
        self.desc = new_name

    # def edit_description(self, new_desc : str) -> None:
    #     self.desc = new_desc

    def mark_complete(self) -> None:
        if len(self.child_objective_list) == 0:
            self.is_complete = True
        else:
            all_children_status = [child.is_complete for child in self.child_objective_list]
            all_children_done = all(all_children_status)
            if all_children_done:
                self.is_complete = True


    def make_subelement(self, name : str):
        new_element = Objective(name=name)
        self.child_objective_list.append(new_element)

        return new_element


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[x]' if self.is_complete else '[ ]'

        obj_string = f'{space}ID: {self._uuid}\n' \
                   f'{space}{self.desc}\n' \
                   f'{space}Is done?: {completion_str}\n' \
                   # f'{space}{self.desc}\n'

        children_list = self.child_objective_list
        if children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string
