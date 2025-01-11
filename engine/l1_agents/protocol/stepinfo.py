from __future__ import annotations

from typing import Optional

from PIL.Image import Image as PILImage

from api import Entry
from engine.l2_models import Options, CallOptions
from engine.l3_aos.workspace import Workspace


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

class Task:
    def __init__(self, content : str):
        self.subtasks : list[Task] = []
        self.content : str = content
        self.is_complete : bool = False

    def complete(self):
        self.is_complete = True

    def add_subtask(self, msg : str):
        new_task = Task(content=msg)
        self.subtasks.append(new_task)
        return new_task

    def get_tree(self, pre_indent : str = '') -> str:
        conditional_mark = 'x' if self.is_complete else ''
        tree = f'{pre_indent}[{conditional_mark}] {self.content}\n'

        for st in self.subtasks:
            indent = '\t' + pre_indent
            tree += f'{st.get_tree(pre_indent=indent)}'

        return tree


class Workflowy(Workspace):
    def close(self, *args, **kwargs):
        pass

    def get_desc(self) -> str:
        pass

    def get_text(self) -> str:
        pass

    def get_image(self) -> Optional[PILImage]:
        return None

    def __init__(self):
        super().__init__()
        self.root_objective : Task = Task()

    def open(self, yaml_str : str):
        pass