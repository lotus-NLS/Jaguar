import uuid

class Task:

    @classmethod
    def make_root_task(cls, name ='', instruction =''):
        this_task = Task(name=name, instruction=instruction)
        this_task.is_root = True

        return this_task

    @classmethod
    def make_sub_task(cls, name ='', instruction =''):
        this_task = Task(name, instruction)
        return this_task

    def __init__(self, name, instruction):
        self.name: str = f'++++ {name} ++++'
        self.instruction: str = f'Instructions: {instruction}'

        self.uuid = f'{uuid.uuid4()}-{uuid.uuid4()}'
        self.is_root = False
        self.children_task_list: list[Task] = []
        self.subtask_dictonary : dict[str,Task] = {}

    def addSubtask(self, title: str = '', desc: str = '-'):
        new_task = Task(name=title, instruction=desc)
        new_task.is_root = False
        self.children_task_list.append(new_task)
        self.subtask_dictonary[new_task.uuid] = new_task

    def __str__(self, indent: int = 0):
        # Indentation logic: based on level of depth (number of indents)
        space = '    ' * indent

        task_str = f'{space}ID: {self.uuid}\n' \
                   f'{space}{self.name}\n' \
                   f'{space}{self.instruction}\n'

        if self.children_task_list:
            task_str += f'{space}Subtasks: \n'
            for child_task in self.children_task_list:
                # Each subtask will handle its own indentation and subtasks recursively
                task_str += child_task.__str__(indent=indent + 1)

        return task_str


# Test driver code
t1 = Task.make_root_task(name='Wash dishes')
t1.addSubtask(title='Pick up soap')
t2 = t1.children_task_list[0]  # Get the "Pick up soap" task
t2.addSubtask(title='Ensure its not empty')  # Add a subtask to "Pick up soap"
t1.addSubtask(title='Scrub the plates')
t1.addSubtask(title='Dry off')

print(t1)
