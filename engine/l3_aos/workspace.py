from __future__ import annotations

import inspect
from abc import abstractmethod, ABC
from typing import Optional, Callable

from PIL.Image import Image as PILImage

from api import Entry
from engine.l3_aos.tools import ToolDoc, ToolArg, Tool, ToolCall
from holytools.devtools import ModuleInspector
from holytools.logging import Loggable

# ---------------------------------------------------------

class Workspace(Loggable):
    def __init__(self):
        super().__init__()
        self.is_active : bool = False
        self.action_factory = WorkspaceToolFactory(workspace=self)
        self.workspace_actions : list[WorkspaceAction] = self.create_workspace_actions()
        self.open_action : WorkspaceAction = self.create_open_action()
        self.close_action : WorkspaceAction = self.create_close_tool()

    def create_workspace_actions(self) -> list[WorkspaceAction]:
        target_methods =  ModuleInspector.get_methods(obj=self, include_inherited=False, include_private=False)
        actions = self.action_factory.create_all(target_methods=target_methods)
        return actions

    def create_open_action(self) -> WorkspaceAction:
        def set_active():
            self.is_active = True
        func = self.open
        return self.action_factory.create_action(mthd=func, hook=set_active)

    def create_close_tool(self) -> WorkspaceAction:
        def set_inactive():
            self.is_active = False
        func = self.close
        return self.action_factory.create_action(mthd=func, hook=set_inactive)

    @abstractmethod
    def open(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        pass

    # ---------------------------------------------------
    # context

    def get_entry(self) -> Entry:
        def big_seperator(name : str) -> str:
            max_len = 50
            num_dashes = max(0, max_len-len(name))
            dashes = '-'*int(num_dashes/2.)
            return '\n+' + dashes + f' {name} '+ dashes + '+\n'

        msg = big_seperator(f'Workspace: \"{self.get_name()}\"')
        msg += self.get_text()
        msg += big_seperator(f'')

        return  Entry.tool(name=self.get_name(), msg=msg, image = self.get_image())


    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_desc(self) -> str:
        pass

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    # ---------------------------------------------------

    def get_actions(self) -> list[WorkspaceAction]:
        while_open = self.workspace_actions + [self.close_action]
        while_closed = [self.open_action]
        return while_open if self.is_active else while_closed

    def get_action_docs(self) -> list[ToolDoc]:
        return [action.get_doc() for action in self.get_actions()]


class WorkspaceToolFactory(Loggable):
    def __init__(self, workspace : Workspace):
        super().__init__()
        self.workspace : Workspace =  workspace

    def create_all(self, target_methods : list[Callable]) -> list[WorkspaceAction]:
        return [self.create_action(mthd=method) for method in target_methods]

    def create_action(self, mthd : Callable, hook : Optional[Callable] = None) -> WorkspaceAction:
        if not inspect.ismethod(mthd):
            raise TypeError(f'{WorkspaceToolFactory.create_action.__name__} only accepts bound methods;'
                            f'Method \"{mthd.__name__}\" is unbound')

        workspace = self.workspace
        conditional_hook = lambda: hook() if hook else None
        docstring = mthd.__doc__

        class NewAction(WorkspaceAction):
            def __init__(self):
                super().__init__(workspace=workspace)
                args = ModuleInspector.get_args(func=mthd)
                self.tool_args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{mthd.__name__}_{workspace.get_name()}'

            def do(self):
                kwargs = {tool_arg.name : tool_arg.get_value() for tool_arg in self.tool_args if tool_arg.is_set()}
                mthd(**kwargs)
                conditional_hook()

            def get_desc(self) -> str:
                desc = docstring if docstring else f'Allows for operating {mthd.__name__}'
                return desc

            def get_args(self) -> list[ToolArg]:
                return self.tool_args
        return NewAction()


class WorkspaceAction(Tool, ABC):
    def __init__(self, workspace: Workspace, call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.workspace : Workspace = workspace

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def _set_args(self, tool_call : ToolCall):
        super()._set_args(tool_call=tool_call)