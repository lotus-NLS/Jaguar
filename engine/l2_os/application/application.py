from typing import Optional, Callable
from engine.l4_tools import Tool, ToolArg, ToolDoc

from .action import Action
from .window import Window, Workspace
from hollarek.core.logging import Loggable, LogSettings
from hollarek.devtools import ModuleInspector
from dataclasses import dataclass
# ---------------------------------------------------

@dataclass
class Application:
    index: int
    workspace_type: type[Workspace]
    desc: str = ''
    max_tabs: Optional[int] = None

    def __post_init__(self):
        self.get_name = lambda : self.workspace_type.__name__
        self.window : Window = Window(index=self.index, app_name=self.get_name())

        action_factory = ActionFactory(cls=self.workspace_type, tab_map=self.window.workspace_map)
        self.actions : list[Action] = action_factory.get_actions()
        self.tool_dict: dict[str, Tool] = {tool.get_name(): tool for tool in self.actions}


    def open(self, uri : Optional[str]):
        if self.max_tabs:
            if len(self.window.workspace_map) == self.max_tabs:
                raise ValueError(f'Cannot open more than {self.max_tabs} tab(s)')

        new_tab = self.workspace_type(uri)
        self.window.add_workspace(new_tab)

    def close(self):
        self.window.close_all()

    # ---------------------------------------------------
    #  actions

    def get_actions(self, active_only : bool= False) -> list[Action]:
        return [action for action in self.actions if action.is_active or not active_only]

    def get_docs(self, active_only : bool = False) -> list[ToolDoc]:
        return [action.get_doc() for action in self.get_actions(active_only=active_only)]

    def is_open(self) -> bool:
        return len(self.window.workspace_map) != 0


class ActionFactory(Loggable):
    def __init__(self, cls : type[Workspace], tab_map : dict[int, Workspace]):
        super().__init__(settings=LogSettings(timestamp=False))
        self.cls : type = cls
        self.tab_map : dict[int, Workspace] =  tab_map
        self.methods : list[Callable] = ModuleInspector.get_methods(cls=self.cls, public_only=True)

    # ---------------------------------------------------------
    # loop

    def get_actions(self) -> list[Action]:
        actions = []
        for method in self.methods:
            excluded_methods = [Workspace.__init__, Workspace.get_text, Workspace.get_image, Workspace.get_desc]
            excluded_method_names = [mthd.__name__ for mthd in excluded_methods]
            if method.__name__ in excluded_method_names:
                continue
            actions.append(self.create_action(mthd=method))
        return actions


    def create_action(self, mthd : Callable) -> Action:
        tab_map = self.tab_map
        args = ModuleInspector.get_args(func=mthd)

        class NewAction(Action):
            def __init__(self):
                super().__init__(tab_map=tab_map)
                self.mthd_args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{self.cls.__name__}_{mthd.__name__}'

            def do(self):
                kwargs = {arg.name : arg.get_value() for arg in self.mthd_args}
                tab = self.get_tab()
                mthd(tab,**kwargs)

            def get_desc(self) -> str:
                return f'Allows for operating {self.get_name()}'

            def get_args(self) -> list[ToolArg]:
                return self.mthd_args + [self.index_arg]

        return NewAction()
