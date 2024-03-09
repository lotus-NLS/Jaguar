from typing import Optional
from engine.l4_tools import Tool, ToolArg

from .action import Action
from .window import Window, Tab
from hollarek.logging import Loggable, LogSettings
from hollarek.devtools import ModuleInspector
# ---------------------------------------------------

class Application:
    def __init__(self, index : int, tab_type : type[Tab], desc : str = ''):
        super().__init__()
        self.index = index
        self.tab_type : type[Tab] = tab_type
        self.get_desc = lambda : desc

        self.window : Window = Window(index=index, name=self.get_name())
        self.actions : list[Action] = self.create_actions()
        self.tool_dict : dict[str, Tool] = {tool.get_name() : tool for tool in self.actions}

    def open(self, path : Optional[str]):
        if not self.window:
            self.window = Window(index=self.index, name=self.get_name())
        new_tab = self.tab_type(path=path)
        self.window.add_tab(new_tab)

    def close(self):
        self.window.close_all()

    # ---------------------------------------------------
    #  actions

    def create_actions(self) -> list[Action]:
        action_factory = ActionFactory(cls=self.tab_type, tab_map=self.window.tab_map)
        return action_factory.get_actions()

    def get_actions(self, active_only : bool= False) -> list[Action]:
        return [action for action in self.actions if action.is_active or not active_only]


    # ---------------------------------------------------
    # documentation

    @classmethod
    def get_name(cls):
        return cls.__name__

    def is_open(self) -> bool:
        return len(self.window.tab_map) != 0



class ActionFactory(Loggable):
    def __init__(self, cls : type[Tab], tab_map : dict[int, Tab]):
        super().__init__(settings=LogSettings(timestamp=False))
        self.cls : type = cls
        self.tab_map : dict[int, Tab] =  tab_map
        self.methods : list[callable] = ModuleInspector.get_methods(cls=self.cls)

    # ---------------------------------------------------------
    # loop

    def get_actions(self) -> list[Action]:
        actions = []
        for method in self.methods:
            name = method.__name__
            if name in [Tab.get_context.__name__, Tab.open.__name__]:
                continue
            actions.append(self.create_action(mthd=method))
        return actions


    def create_action(self, mthd : callable) -> Action:
        tab_map = self.tab_map
        args = ModuleInspector.get_args(func=mthd)

        class NewAction(Action):
            def __init__(self):
                super().__init__(tab_map=tab_map)
                self.args: list[ToolArg] = [ToolArg.from_function_arg(arg) for arg in args]

            @classmethod
            def get_name(cls) -> str:
                return f'{mthd.__name__}'

            def do(self):
                kwargs = {name : arg.get_value() for name,arg in self.get_args()}
                mthd(**kwargs)

            def get_desc(self) -> str:
                return f'Allows for operating {self.get_name()}'

            def get_args(self) -> list[ToolArg]:
                return self.args

        return NewAction()
