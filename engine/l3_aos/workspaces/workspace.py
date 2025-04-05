from __future__ import annotations

import inspect
from abc import abstractmethod
from typing import Optional, Callable

from PIL.Image import Image as PILImage

from engine.l3_aos.tools import ToolDoc, ToolArg, Tool
from holytools.devtools import ModuleInspector
from holytools.logging import Timber

# ---------------------------------------------------------

class Workspace(Timber):
    def __init__(self):
        super().__init__()
        self.is_active : bool = False
        self.workspace_actions : list[Tool] = self.create_workspace_actions()
        self.open_action : Tool = self.create_action(mthd=self.open)
        self.close_action : Tool = self.create_action(mthd=self.close)

    @abstractmethod
    def open(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        pass

    def create_workspace_actions(self) -> list[Tool]:
        target_methods =  ModuleInspector.get_methods(obj=self, include_inherited=False, include_private=False)
        actions = [self.create_action(mthd=m) for m in target_methods]
        return actions

    def create_action(self, mthd : Callable) -> Tool:
        if not inspect.ismethod(mthd):
            raise TypeError(f'{self.create_action.__name__} only accepts bound method, method \"{mthd.__name__}\" is unbound')

        workspace = self
        docstring = mthd.__doc__

        class WorkspaceAction(Tool):
            def __init__(self):
                super().__init__()
                args = ModuleInspector.get_args(func=mthd)
                self.tool_args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{workspace.get_name()}_{mthd.__name__}'

            def _do(self):
                kwargs = {tool_arg.name : tool_arg.get_value() for tool_arg in self.tool_args if tool_arg.is_set()}
                mthd(**kwargs)
                if mthd.__name__ == workspace.open.__name__:
                    workspace.is_active = True
                if mthd.__name__ == workspace.close.__name__:
                    workspace.is_active = False

            def get_desc(self) -> str:
                desc = docstring if docstring else ''
                return desc

            def get_args(self) -> list[ToolArg]:
                return self.tool_args

        return WorkspaceAction()

    def get_actions(self) -> list[Tool]:
        while_open = self.workspace_actions + [self.close_action]
        while_closed = [self.open_action]
        return while_open if self.is_active else while_closed

    def get_action_docs(self) -> list[ToolDoc]:
        return [action.get_doc() for action in self.get_actions()]

    # ---------------------------------------------------

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    @classmethod
    def get_desc(cls) -> str:
        return cls.__doc__
