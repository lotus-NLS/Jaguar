import uuid

# ----------------------------------------------------


class AgendaEntry:
    @classmethod
    def make_root(cls, name, instruction):
        return cls(name,instruction,is_root=True)

    def __init__(self,name, instruction, is_root = False):
        self.name: str = f'++++ {name} ++++'
        self.desc: str = f'Instructions: {instruction}'
        self.is_complete : bool = False

        self._uuid = f'{uuid.uuid4()}-{uuid.uuid4()}'
        self._is_root = is_root
        self.subelement_dictionary : dict[str, AgendaEntry] = {}

        self.actions = [self.edit_name, self.edit_description, self.mark_complete, self.add_subelement]


    def edit_name(self, new_name : str):
        self.name = new_name

    def edit_description(self, new_desc : str):
        self.desc = new_desc

    def mark_complete(self):
        self.is_complete = True

    def add_subelement(self, name : str, instruction: str):
        new_element = AgendaEntry(name=name, instruction=instruction)
        new_element._is_root = False
        self.subelement_dictionary[new_element._uuid] = new_element


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[x]' if self.is_complete else '[ ]'

        obj_string = f'{space}ID: {self._uuid}\n' \
                   f'{space}{self.name}\n' \
                   f'{space}Is root?: {self._is_root}\n' \
                   f'{space}Is done?: {completion_str}\n' \
                   f'{space}{self.desc}\n'

        children_list = self.subelement_dictionary.values()
        if children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string


class Task(AgendaEntry):
    pass

class Objective(AgendaEntry):
    pass


