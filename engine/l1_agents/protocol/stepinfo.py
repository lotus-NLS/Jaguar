from __future__ import annotations

import sys
from io import StringIO
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


class Objective:
    def __init__(self, content : str, identifier : str = '', is_root : bool = False):
        self.is_root : bool = is_root
        self.content : str = content
        self.identifier : str = identifier

        self.is_complete : bool = False
        self.subtasks : list[Objective] = []

    def get_descendant(self, identifier : str) -> Objective:
        if len(identifier) == 0:
            return self

        first_num = int(identifier[0])
        partial_id = identifier[1:]
        return self.subtasks[first_num-1].get_descendant(partial_id)


    def complete(self):
        self.is_complete = True
        for st in self.subtasks:
            st.complete()

    def add_subtask(self, msg : str):
        new_task = Objective(content=msg, identifier=f'{self.identifier}{len(self.subtasks)+1}')
        self.subtasks.append(new_task)
        return new_task

    def get_tree(self, pre_indent : str = '') -> str:
        if not self.is_root:
            conditional_mark = 'x' if self.is_complete else ' '
            tree = f'{pre_indent}[{conditional_mark}] {self.identifier}: {self.content}\n'
        else:
            tree = ''

        for st in self.subtasks:
            indent = '\t' + pre_indent if not self.is_root else ''
            tree += f'{st.get_tree(pre_indent=indent)}'

        return tree


class Workflowy(Workspace):
    def __init__(self):
        super().__init__()
        self.root_objective : Optional[Objective] = None

    def _is_active(self) -> bool:
        return not self.root_objective is None

    def add(self, task_id : str, msg : str):
        parent = self.root_objective.get_descendant(task_id)
        parent.add_subtask(msg)

    def complete(self, task_id : str):
        self.root_objective.get_descendant(task_id).complete()

    def delete(self, task_id : str):
        partial_id = task_id[:-1]
        parent = self.root_objective.get_descendant(partial_id)
        del parent.subtasks[int(task_id[-1])]

    # -------------------------------
    # Generics

    def open(self, yaml_str : str):
        self.root_objective = Objective(content='', is_root=True)

    def close(self, *args, **kwargs):
        self.root_objective = None

    def get_desc(self) -> str:
        return f'Provides a task list with subtask functionality. Tasks can be added, completed and deleted'

    def get_text(self) -> str:
        return self.root_objective.get_tree()

    def get_image(self) -> Optional[PILImage]:
        return None



if __name__ == "__main__":
    def input_generator():
        yield "20"
        yield ""

    gen = input_generator()

    def simulated_input():
        return next(gen)

    import builtins
    builtins.input = simulated_input

    from holytools.userIO import CLI
    cli = CLI(Workflowy)
    cli.command_loop()