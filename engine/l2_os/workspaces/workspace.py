from __future__ import annotations
from abc import abstractmethod, ABC
from PIL.Image import Image as PILImage
from api import Entry
from typing import Optional, Callable, Any
import inspect

from engine.l4_tools import ToolArg, ToolDoc, Tool, ToolCall
from hollarek.core.logging import Loggable, LogSettings
from hollarek.devtools import ModuleInspector
# ---------------------------------------------------------

class Workspace(Loggable):
    def __init__(self):
        super().__init__()
        self.action_factory = ActionFactory(workspace=self)
        self.is_active : bool = False
        self.workspace_actions : list[Action] = self.create_workspace_actions()
        self.open_action : Action = self.create_open_action()
        self.close_action : Action = self.create_close_action()

    def create_workspace_actions(self) -> list[Action]:
        cls_mthds =  ModuleInspector.get_methods(obj=self.__class__, include_inherited=False, public_only=True)
        excluded_names = [func.__name__ for func in ModuleInspector.get_methods(obj=Workspace)]
        target_methods = [mthd for mthd in cls_mthds if not mthd.__name__ in excluded_names]
        actions = self.action_factory.create_all(target_methods=target_methods)
        return actions

    def create_open_action(self) -> Action:
        def set_active():
            self.is_active = True
        func = self.__class__.on_open
        func.__name__ = f'open'
        return self.action_factory.create_action(mthd=func, hook=set_active)

    def create_close_action(self) -> Action:
        def set_inactive():
            self.is_active = False
        func = self.__class__.on_close
        func.__name__ = f'close'
        return self.action_factory.create_action(mthd=func, hook=set_inactive)

    @abstractmethod
    def on_open(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_close(self, *args, **kwargs):
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

        return  Entry.as_tool(name=self.get_name(), msg=msg, image = self.get_image())


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

    def get_actions(self):
        return self.workspace_actions + [self.close_action] if self.is_active else [self.open_action]

    def get_docs(self) -> list[ToolDoc]:
        return [action.get_doc() for action in self.get_actions()]


class ActionFactory(Loggable):
    def __init__(self, workspace : Workspace):
        super().__init__(settings=LogSettings(timestamp=False))
        self.workspace : Workspace =  workspace

    def create_all(self, target_methods : list[Callable]) -> list[Action]:
        return [self.create_action(mthd=method) for method in target_methods]

    def create_action(self, mthd : Callable, hook : Optional[Callable[[], Any]] = None) -> Action:
        if inspect.ismethod(mthd):
            raise TypeError(f'{ActionFactory.create_action.__name__} accept only unbound methods;'
                            f'Method \"{mthd.__name__}\" is bound')

        workspace = self.workspace
        conditional_hook = lambda: hook() if hook else None
        docstring = mthd.__doc__

        class NewAction(Action):
            def __init__(self):
                super().__init__(workspace=workspace)
                args = ModuleInspector.get_args(func=mthd)
                self.tool_args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{mthd.__name__}_{workspace.get_name()}'

            def do(self):
                kwargs = {tool_arg.name : tool_arg.get_value() for tool_arg in self.tool_args if tool_arg.is_set()}
                mthd(workspace, **kwargs)
                conditional_hook()

            def get_desc(self) -> str:
                desc = docstring if docstring else f'Allows for operating {mthd.__name__}'
                return desc

            def get_args(self) -> list[ToolArg]:
                return self.tool_args
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
