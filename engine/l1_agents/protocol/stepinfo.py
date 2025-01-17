from __future__ import annotations

from typing import Optional

from PIL.Image import Image as PILImage

from api import Entry
from engine.l2_models import Options, CallOptions
from engine.l3_aos.workspace import Workspace


# ------------------------------------------------------------------------

class StepInfo:
    def __init__(self, memory : Optional[Entry] = None, notice :  Optional[Entry] = None, required_tool_name : Optional[str] = None):
        self.memory_update : Entry = memory
        self.notice : Entry = notice
        self.required_tool : Optional[str] = required_tool_name

    @classmethod
    def make_default(cls, msg : str):
        return cls(memory=Entry.user(msg=msg))

    def get_options(self) -> Options:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.required_tool)
        return Options(call_options=call_options)


class Workflowy(Workspace):
    def __init__(self):
        super().__init__()
        self.root : Optional[Task] = None

    def add(self, task_id : str, msg : str):
        parent = self.root.get_descendant(task_id)
        parent.add_subtask(msg)

    def complete(self, task_id : str):
        self.root.get_descendant(task_id).complete()

    def delete(self, task_id : str):
        partial_id = task_id[:-1]
        parent = self.root.get_descendant(partial_id)
        del parent.subtasks[int(task_id[-1])]

    # -------------------------------
    # Generics

    def open(self):
        # self.root = Task(content='', is_root=True)
        #TODO: This is for testing purposes
        self.root = self._get_test_task()

    @classmethod
    def _get_test_task(cls):
        root = Task(is_root=True)
        t1 = root.add_subtask(msg=f'Provide user with summary of hardware')
        t1.add_subtask(msg=f'Make a list of all information I think the user requires')
        t1.add_subtask(msg=f'Acquire information')
        t1.add_subtask(msg=f'Write out summary')
        return root

    def close(self, *args, **kwargs):
        self.root = None

    def get_desc(self) -> str:
        return f'Provides a task list with subtask functionality. Tasks can be added, completed and deleted'

    def get_text(self) -> str:
        return (f'You are currently engaged in work mode. The user is not present and what you write will only be visible to you.\n'
                f'These are your tasks:\n'
                f'{self.root.get_tree()}'
                f'Upon completing these tasks you will automatically return to conversation mode')

    def get_image(self) -> Optional[PILImage]:
        return None


class Task:
    def __init__(self, content : str = '', identifier : str = '', is_root : bool = False):
        self.is_root : bool = is_root
        self.name : str = content
        self.identifier : str = identifier

        self.is_complete : bool = False
        self.subtasks : list[Task] = []

    @classmethod
    def from_yaml(cls, s : str):
        lines = s.split('\n')
        root = Task(is_root=True)
        ancestors = [root]

        def get_ancestor_indent():
            return len(ancestors) - 2

        for l in lines:
            indentation = len(l) - len(l.lstrip(' '))
            if indentation > get_ancestor_indent() + 1:
                raise ValueError(f'Indentation error at line: {l}')

            while indentation < get_ancestor_indent() + 1:
                ancestors.pop()
            if indentation == get_ancestor_indent() + 1:
                a = ancestors[-1]
                new = a.add_subtask(msg=l.strip(' -'))
                ancestors.append(new)
        return root

    def add_subtask(self, msg : str):
        new_task = Task(content=msg, identifier=f'{self.identifier}{len(self.subtasks) + 1}')
        self.subtasks.append(new_task)
        return new_task


    def get_descendant(self, identifier : str) -> Task:
        if len(identifier) == 0:
            return self

        first_num = int(identifier[0])
        partial_id = identifier[1:]

        return self.subtasks[first_num-1].get_descendant(partial_id)

    def complete(self):
        self.is_complete = True
        for st in self.subtasks:
            st.complete()

    def get_tree(self, pre_indent : str = '') -> str:
        if not self.is_root:
            conditional_mark = 'x' if self.is_complete else ' '
            tree = f'{pre_indent}[{conditional_mark}] {self.identifier}: {self.name}\n'
        else:
            tree = ''

        for st in self.subtasks:
            indent = '\t' + pre_indent if not self.is_root else ''
            tree += f'{st.get_tree(pre_indent=indent)}'

        return tree


if __name__ == "__main__":
    wf = Workflowy()
    wf.open()

    print(wf.root.get_tree())
    wf.complete(task_id='11')