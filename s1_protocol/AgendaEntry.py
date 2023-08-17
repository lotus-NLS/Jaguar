import uuid

# ----------------------------------------------------

class AgendaEntry:
    @classmethod
    def make_root(cls, name, instruction):
        return cls(name,instruction,is_root=True)

    def __init__(self,name, instruction, is_root = False):
        self.name: str = f'++++ {name} ++++'
        self.desc: str = f'Instructions: {instruction}'
        self.is_complete = False

        self._uuid = f'{uuid.uuid4()}-{uuid.uuid4()}'
        self._is_root = is_root
        self.children_list: list[AgendaEntry] = []
        self.subelement_dictionary : dict[str, AgendaEntry] = {}

    def edit_name(self, new_name):
        self.name = new_name

    def edit_description(self, new_desc):
        self.desc = new_desc

    def mark_complete(self):
        self.is_complete = True

    def _add_subelement(self, name : str, instruction: str):
        new_element = AgendaEntry(name=name, instruction=instruction)
        new_element._is_root = False
        self.children_list.append(new_element)
        self.subelement_dictionary[new_element._uuid] = new_element


    def __str__(self, indent: int = 0):
        space = '    ' * indent
        completion_str = '[x]' if self.is_complete else '[ ]'

        obj_string = f'{space}ID: {self._uuid}\n' \
                   f'{space}{self.name}\n' \
                   f'{space}Is root?: {self._is_root}\n' \
                   f'{space}Is done?: {completion_str}\n' \
                   f'{space}{self.desc}\n'

        if self.children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in self.children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string


class Task(AgendaEntry):
    def add_subtask(self, name, instruction):
        return self._add_subelement(name,instruction)


class Objective(AgendaEntry):
    def add_subobjective(self, name, instruction):
        return self._add_subelement(name, instruction)



# Example usage:
root_task = Task.make_root("Complete project", "Finish the software project by end of month.")
root_task.add_subtask("Write code", "Implement the main features.")
root_task.add_subtask("Test", "Make sure there are no bugs.")
print(root_task)

root_objective = Objective.make_root("Increase user engagement", "Aim for 20% more daily active users.")
root_objective.add_subobjective("Optimize UI", "Redesign the main landing page for better user experience.")
print(root_objective)
