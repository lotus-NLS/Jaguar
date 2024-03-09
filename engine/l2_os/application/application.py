from typing import Optional, Callable
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

        self.window : Window = Window(index=index, app_name=self.get_name())
        self.actions : list[Action] = self.create_actions()
        self.tool_dict : dict[str, Tool] = {tool.get_name() : tool for tool in self.actions}

    def open(self, uri : Optional[str]):
        if not self.window:
            self.window = Window(index=self.index, app_name=self.get_name())
        new_tab = self.tab_type(uri=uri)
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
        self.methods : list[Callable] = ModuleInspector.get_methods(cls=self.cls)

    # ---------------------------------------------------------
    # loop

    def get_actions(self) -> list[Action]:
        actions = []
        for method in self.methods:
            excluded_methods = [Tab.get_entry, Tab.__init__, Tab.get_text, Tab.get_text, Tab.get_image]
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
                return f'{mthd.__name__}'

            def do(self):
                kwargs = {arg.name : arg.get_value() for arg in self.mthd_args}
                # print(f'kwargs are {kwargs}')
                tab = self.get_tab()
                mthd(tab,**kwargs)

            def get_desc(self) -> str:
                return f'Allows for operating {self.get_name()}'

            def get_args(self) -> list[ToolArg]:
                return self.mthd_args + [self.index_arg]

        return NewAction()
