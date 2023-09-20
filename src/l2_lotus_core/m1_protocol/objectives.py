import uuid

# ----------------------------------------------------


class Objective:
    @classmethod
    def make_root(cls, name : str, instruction_text : str):
        return cls(name, instruction_text, is_root=True)

    def __init__(self, name : str, instruction_text : str, is_root = False):
        self.name: str = f'++++ {name} ++++'
        # self.desc: str = f'Instructions: {instruction_text}'
        self.is_complete : bool = False

        self._uuid = f'{uuid.uuid4()}'
        self._is_root = is_root
        self.subelement_dictionary : dict[str, Objective] = {}

        self.actions = [self.edit_name, self.mark_complete, self.add_subelement]

    def is_done(self) -> bool:
        return self.is_complete

    def is_root(self) -> bool:
        return self._is_root

    def edit_name(self, new_name : str) -> None:
        self.name = new_name

    # def edit_description(self, new_desc : str) -> None:
    #     self.desc = new_desc

    def mark_complete(self) -> None:
        if len(self.subelement_dictionary) == 0:
            self.is_complete = True
        else:
            all_children_status = [child.is_complete for child in self.subelement_dictionary.values()]
            all_children_done = all(all_children_status)
            if all_children_done:
                self.is_complete = True


    def add_subelement(self, name : str, instruction: str):
        new_element = Objective(name=name, instruction_text=instruction)
        new_element._is_root = False
        self.subelement_dictionary[new_element._uuid] = new_element


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[x]' if self.is_complete else '[ ]'

        obj_string = f'{space}ID: {self._uuid}\n' \
                   f'{space}{self.name}\n' \
                   f'{space}Is root?: {self._is_root}\n' \
                   f'{space}Is done?: {completion_str}\n' \
                   # f'{space}{self.desc}\n'

        children_list = self.subelement_dictionary.values()
        if children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string
