from __future__ import annotations

from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.tools import Tool
from engine.l3_aos.workspaces import Workspace


# -------------------------------------------------------

class TaskTracker(Workspace):
    """This workspace provides a task list with subtask functionality. Each task is assigned a task_id e.g. 12 for the second subtask of the first task."""
    def __init__(self):
        super().__init__()
        self.root : Optional[Task] = None
        self.headline : Optional[str] = None
        self.report_query : str = (
            f'Now leaving work mode. Please review the objective and provide an execute summary of your results '
            f'with regard to this objective. Keep it to 60 words or less, so about 3-4 sentences.'
            f'This report will be used to evaluate the success or failure of the objective.')

        self.work_notice : str = (f'You are currently in work mode and cannot converse with the user. '
                       f'Your current tasks are outlined in the {self.__class__.__name__} workspace. '
                       f'The only active instance of TaskTracker workspace is marked with ** {self.__class__.__name__} (Active) ** '
                       f'Upon completing these tasks or closing the workspace you will automatically'
                       f' return to conversation mode')
        self.update_tool : Tool = self.create_action(mthd=self.update)



    def update(self, action_headline : str):
        """Allows you to report the actions youve taken since your last call of this update tool. Collectively these updates generate a timeline of your actions. Focus on your actions rather than the results. The results will be discussed in a report later on"""
        self.headline : str = action_headline

    def add_task(self, parent_task_id : str, msg : str):
        """Adds a subtask to parent task with [parent_task_id] e.g. parent_task_id adds new task with [msg] to first top level task"""
        parent = self.root.get_descendant(parent_task_id)
        parent.add_subtask(msg)

    def add_comment(self, task_id : str, msg : str):
        """Adds a comment to task [task_id]. Use this to store updates, relevant information or reason about why this task should be marked as done or discarded"""
        self.root.get_descendant(task_id).add_comment(msg)

    def complete_task(self, task_id : str):
        """Completes task [task_id]"""
        self.root.get_descendant(task_id).complete()

    def fail_task(self, task_id : str):
        """Marks [task_id] as failed, unnecessary or discarded"""
        self.root.get_descendant(task_id).fail()

    # -------------------------------
    # Generics


    def get_actions(self) -> list[Tool]:
        actions = super().get_actions()
        return [a for a in actions if a.get_name() != self.update_tool.get_name()]

    def open(self):
        """Opens task tracker"""
        self.root = Task(content='', is_root=True)

    def close(self):
        """Closes task tracker"""
        self.root = None

    def get_text(self) -> str:
        return f'Current tasks:\n{self.root.get_tree()}'

    def get_image(self) -> Optional[PILImage]:
        return None


class Task:
    def __init__(self, content : str = '', identifier : str = '', is_root : bool = False):
        self.is_root : bool = is_root
        self.name : str = content
        self.identifier : str = identifier

        self.comment : str = ''
        self.is_complete : bool = False
        self.is_failed : bool = False
        self.subtasks : list[Task] = []

    def recursively_complete(self) -> bool:
        if not self.subtasks:
            return self.is_complete
        else:
            return all(st.recursively_complete() for st in self.subtasks)


    @classmethod
    def get_example(cls) -> Task:
        return cls.from_yaml(s=f'- Example')

    @classmethod
    def from_yaml(cls, s : str) -> Task:
        lines = s.split('\n')
        root = Task(is_root=True)
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

    def add_comment(self, msg : str):
        self.comment += msg

    def add_subtask(self, msg : str) -> Task:
        new_task = Task(content=msg, identifier=f'{self.identifier}{len(self.subtasks) + 1}')
        self.subtasks.append(new_task)
        return new_task

    def complete(self):
        self.is_complete = True
        for st in self.subtasks:
            st.complete()

    def fail(self):
        self.is_failed = True
        for st in self.subtasks:
            st.fail()

    # --------------------------------------------
    # get

    def get_descendant(self, identifier : str) -> Task:
        if len(identifier) == 0:
            return self

        first_num = int(identifier[0])
        partial_id = identifier[1:]

        parrent_idx = first_num-1
        if parrent_idx < 0:
            raise ValueError(f'Invalid task id: {identifier}. Must be greater than 0')

        return self.subtasks[parrent_idx].get_descendant(partial_id)

    def get_tree(self, pre_indent : str = '') -> str:
        if not self.is_root:
            if self.is_complete:
                mark = 'x'
            elif self.is_failed:
                mark = '🚫'
            else:
                mark = ' '
            status_and_id = f'[{mark}] {self.identifier}: '
            tree = f'{pre_indent}{status_and_id}{self.name}\n'
            if self.comment:
                tree += f'{pre_indent}{len(status_and_id)*" "}{self.comment}\n'
        else:
            tree = ''

        for st in self.subtasks:
            indent = '\t' + pre_indent if not self.is_root else ''
            tree += f'{st.get_tree(pre_indent=indent)}'

        return tree