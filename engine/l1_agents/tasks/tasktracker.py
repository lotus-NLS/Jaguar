from __future__ import annotations

from typing import Optional

from PIL.Image import Image as PILImage

from engine.l1_agents.tasks.task import Task
from engine.l3_aos.tools import Tool
from engine.l3_aos.workspaces import Workspace


# -------------------------------------------------------

class TaskTracker(Workspace):
    """This workspace provides a task list with subtask functionality. Each task is assigned a task_id e.g. 12 for the second subtask of the first task."""
    def __init__(self):
        super().__init__()
        self.root : Optional[Task] = None
        self.headline : Optional[str] = None
        self.work_notice : str = (f'You are currently in work mode and cannot converse with the user. '
                       f'Your current tasks are outlined in the {self.__class__.__name__} workspace. '
                       f'The only active instance of Tracker workspace is marked with ** {self.__class__.__name__} (Active) ** '
                       f'Upon completing these tasks or closing the workspace you will automatically'
                       f' return to conversation mode')
        self.update_tool : Tool = self.create_action(mthd=self.update)



    def update(self, action_headline : str):
        """Allows you to report the actions youve taken since your last call of this update tool. Collectively these updates generate a timeline of your actions. Focus on your actions rather than the results. The results will be discussed in a report later on"""
        self.headline : str = action_headline

    def add_comment(self, task_id : str, msg : str):
        """Adds a comment to task [task_id]. Use this to store updates, relevant information or reason about why this task should be marked as done or discarded"""
        self.root.get_descendant(task_id).add_comment(msg)

    def complete_task(self, task_id : str):
        """Completes task [task_id]"""
        self.root.get_descendant(task_id).complete()

        is_working = not self.root.is_recursively_handled()
        if not is_working:
            self.close_action.execute(args_dict={})

    def retry(self, task_id : str):
        """Marks [task_id] in need of retry. A retry routine will be initiated later on"""
        self.root.get_descendant(task_id).retry()

    # -------------------------------
    # Generics

    @classmethod
    def is_system_opened(cls) -> bool:
        return True

    def get_actions(self) -> list[Tool]:
        actions = super().get_actions()
        return [a for a in actions if a.get_name() != self.update_tool.get_name()]

    def open(self):
        """Opens task tracker"""
        if self.root is None:
            raise ValueError('Root task is not initialized. Please initialize it with a task before opening')

    def close(self):
        """Closes task tracker"""
        self.root = None

    def get_text(self) -> str:
        return f'Current tasks:\n{self.root.get_tree()}'

    def get_image(self) -> Optional[PILImage]:
        return None

