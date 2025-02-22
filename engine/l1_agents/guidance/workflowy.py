from __future__ import annotations

from typing import Optional
from PIL.Image import Image as PILImage
from engine.l3_aos.workspace import Workspace

# -------------------------------------------------------

class Workflowy(Workspace):
    def __init__(self):
        super().__init__()
        self.root : Optional[Mandate] = None

    def add_task(self, parent_task_id : str, msg : str):
        """Adds a subtask to parent task with [parent_task_id]"""
        parent = self.root.get_descendant(parent_task_id)
        parent.add_subtask(msg)

    def complete_task(self, task_id : str):
        """Completes task [task_id]"""
        self.root.get_descendant(task_id).complete()

    def fail_task(self, task_id : str):
        """Marks [task_id] as failed, unnecessary or discarded"""
        self.root.get_descendant(task_id).fail()

    # -------------------------------
    # Generics

    def open(self):
        self.root = Mandate(content='', is_root=True)

    def close(self, *args, **kwargs):
        self.root = None

    def get_desc(self) -> str:
        return (f'Provides a task list with subtask functionality. '
                f'Each task is assigned a task_id e.g. 12 for the second subtask of the first task.')

    def get_text(self) -> str:
        return (f'You are currently engaged in work mode. The user is not present and what you write will only be visible to you.\n'
                f'These are your tasks:\n'
                f'{self.root.get_tree()}'
                f'Upon completing these tasks you will automatically return to conversation mode')

    def get_image(self) -> Optional[PILImage]:
        return None

class Mandate:
    def __init__(self, content : str = '', identifier : str = '', is_root : bool = False):
        self.is_root : bool = is_root
        self.name : str = content
        self.identifier : str = identifier

        self.is_complete : bool = False
        self.is_failed : bool = False
        self.subtasks : list[Mandate] = []

    @classmethod
    def from_yaml(cls, s : str):
        lines = s.split('\n')
        root = Mandate(is_root=True)
        ancestors = [root]

        def get_ancestor_indent():
            return len(ancestors) - 2

        for l in lines:
            blank_spaces = len(l) - len(l.lstrip(' '))
            if not blank_spaces % 4 == 0:
                raise ValueError(f'Indentation error at line: {l}. Indentation must be multiple of 4, is {blank_spaces}')
            indentation = blank_spaces // 4
            if indentation > get_ancestor_indent() + 1:
                raise ValueError(f'Indentation is more than two increments larger than parent at line: {l}')

            while indentation < get_ancestor_indent() + 1:
                ancestors.pop()
            if indentation == get_ancestor_indent() + 1:
                a = ancestors[-1]
                new = a.add_subtask(msg=l.strip(' -'))
                ancestors.append(new)
        return root

    def add_subtask(self, msg : str):
        new_task = Mandate(content=msg, identifier=f'{self.identifier}{len(self.subtasks) + 1}')
        self.subtasks.append(new_task)
        return new_task


    def get_descendant(self, identifier : str) -> Mandate:
        if len(identifier) == 0:
            return self

        first_num = int(identifier[0])
        partial_id = identifier[1:]

        return self.subtasks[first_num-1].get_descendant(partial_id)

    def complete(self):
        self.is_complete = True
        for st in self.subtasks:
            st.complete()

    def fail(self):
        self.is_failed = True
        for st in self.subtasks:
            st.fail()

    def get_tree(self, pre_indent : str = '') -> str:
        if not self.is_root:
            if self.is_complete:
                mark = '✗'
            elif self.is_failed:
                mark = '🚫'
            else:
                mark = ' '
            tree = f'{pre_indent}[{mark}] {self.identifier}: {self.name}\n'
        else:
            tree = ''

        for st in self.subtasks:
            indent = '\t' + pre_indent if not self.is_root else ''
            tree += f'{st.get_tree(pre_indent=indent)}'

        return tree