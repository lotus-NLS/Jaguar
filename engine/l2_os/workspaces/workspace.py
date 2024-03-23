from __future__ import annotations
from abc import abstractmethod, ABC
from PIL.Image import Image as PILImage
from api import Entry
from typing import Optional, Callable

from engine.l4_tools import ToolArg, ToolDoc, Tool, ToolCall
from hollarek.core.logging import Loggable, LogSettings
from hollarek.devtools import ModuleInspector

# ---------------------------------------------------------

class Workspace(Loggable):
    def __init__(self):
        super().__init__()
        self.action_factory = ActionFactory(workspace=self)
        self.is_active : bool = False

    def open(self):
        self.is_active = True

    def close(self):
        self.is_active = False

    def get_entry(self) -> Entry:
        msg = f'Workspace: \"{self.get_name()}\"'
        msg += self.get_text()
        return Entry.as_tool(name=self.get_name(), msg=msg, image = self.get_image())

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    # ---------------------------------------------------

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    def get_actions(self) -> list[Action]:
        if self.is_active:
            base_methods = ModuleInspector.get_methods(obj=self)
            excluded_methods = [func for func in base_methods if not func in [Workspace.close]]
            actions = self.action_factory.create_all(excluded_methods=excluded_methods)
        else:
            actions = [self.action_factory.create_action(mthd=self.open)]
        return actions

    def get_docs(self) -> list[ToolDoc]:
        return [action.get_doc() for action in self.get_actions()]


class ActionFactory(Loggable):
    def __init__(self, workspace : Workspace):
        super().__init__(settings=LogSettings(timestamp=False))
        self.workspace : Workspace =  workspace
        self.methods : list[Callable] = ModuleInspector.get_methods(obj=workspace, public_only=True)

    # ---------------------------------------------------------
    # loop

    def create_all(self, excluded_methods : list[Callable]) -> list[Action]:
        actions = []
        for method in self.methods:
            excluded_method_names = [mthd.__name__ for mthd in excluded_methods]
            if method.__name__ in excluded_method_names:
                continue
            actions.append(self.create_action(mthd=method))
        return actions


    def create_action(self, mthd : Callable) -> Action:
        args = ModuleInspector.get_args(func=mthd)
        workspace = self.workspace

        class NewAction(Action):
            def __init__(self):
                super().__init__(workspace=workspace)
                self.mthd_args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{workspace.get_name()}_{mthd.__name__}'

            def do(self):
                kwargs = {arg.name : arg.get_value() for arg in self.mthd_args}
                mthd(**kwargs)

            def get_desc(self) -> str:
                return f'Allows for operating {self.get_name()}'

            def get_args(self) -> list[ToolArg]:
                return self.mthd_args

        return NewAction()


class Action(Tool, ABC):
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
