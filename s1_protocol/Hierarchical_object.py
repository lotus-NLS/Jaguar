import uuid

class Hierarchical_object:

    @classmethod
    def make_root_object(cls, name ='', instruction =''):
        this_obj = Hierarchical_object(name=name, instruction=instruction)
        this_obj.is_root = True

        return this_obj

    @classmethod
    def make_sub_element(cls, name ='', instruction =''):
        this_task = Hierarchical_object(name, instruction)
        return this_task

    def __init__(self, name, instruction):
        self.name: str = f'++++ {name} ++++'
        self.instruction: str = f'Instructions: {instruction}'

        self.uuid = f'{uuid.uuid4()}-{uuid.uuid4()}'
        self.is_root = False
        self.children_list: list[Hierarchical_object] = []
        self.subelement_dictionary : dict[str, Hierarchical_object] = {}

    def add_subelement(self, title: str = '', desc: str = '-'):
        new_element = Hierarchical_object(name=title, instruction=desc)
        new_element.is_root = False
        self.children_list.append(new_element)
        self.subelement_dictionary[new_element.uuid] = new_element

    def __str__(self, indent: int = 0):
        space = '    ' * indent

        obj_string = f'{space}ID: {self.uuid}\n' \
                   f'{space}{self.name}\n' \
                   f'{space}{self.instruction}\n'

        if self.children_list:
            obj_string += f'{space}Subtasks: \n'
            for child_task in self.children_list:
                obj_string += child_task.__str__(indent=indent + 1)

        return obj_string





# Test driver code
t1 = Hierarchical_object.make_root_object(name='Wash dishes')
t1.add_subelement(title='Pick up soap')
t2 = t1.children_list[0]  # Get the "Pick up soap" task
t2.add_subelement(title='Ensure its not empty')  # Add a subtask to "Pick up soap"
t1.add_subelement(title='Scrub the plates')
t1.add_subelement(title='Dry off')

print(t1)
