from typing import Optional
from abc import abstractmethod
from engine.l4_tools import Tool, ToolArg

from dataclasses import dataclass
from .action import Action
from .window import Window, Tab

# ---------------------------------------------------

class Application:
    def __init__(self, index : int, tab_type : type[Tab]):
        super().__init__()
        self.index = index
        self.tab_type : type[Tab] = tab_type

        self.window : Window = Window(index=index, name=self.get_name())
        self.actions : list[Action] = self.create_actions()
        self.tool_dict : dict[str, Tool] = {tool.get_name() : tool for tool in self.actions}

    def open(self, path : Optional[str]):
        if not self.window:
            self.window = Window(index=self.index, name=self.get_name())
        new_tab = self.tab_type(path=path)
        self.window.add_tab(new_tab)

    def close(self):
        self.window = None
        self.actions = self.create_actions()

    # ---------------------------------------------------
    #  actions

    def create_actions(self) -> list[Action]:
        action_factory = ActionFactory(cls=self.tab_type, app_name=self.get_name())
        return action_factory.get_actions()

    def get_actions(self, active_only : bool= False) -> list[Action]:
        return [action for action in self.actions if action.is_active or not active_only]


    # ---------------------------------------------------
    # documentation

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    @abstractmethod
    def get_desc(cls):
        pass

    def is_open(self) -> bool:
        return len(self.window.tabs) != 0


import inspect
from hollarek.logging import Loggable, LogSettings, LogLevel
# ---------------------------------------------------------

@dataclass
class Argument:
    name : str
    dtype : type


class ActionFactory(Loggable):
    def __init__(self, cls : type[Tab], app_name : str):
        super().__init__(settings=LogSettings(timestamp=False))
        self.cls : type = cls
        self.app_name : str = app_name
        self.methods_dict : dict[int, callable] = get_methods_map(cls=self.cls)

    # ---------------------------------------------------------
    # loop

    # def get_actions(self) -> list[Action]:
    #     class




    @staticmethod
    def get_value(user_input : str, arg_type : type, arg_name : str):
        if arg_type == bool:
            if user_input not in ['0', '1']:
                raise ValueError(f"For argument '{arg_name}', please enter '0' for False or '1' for True.")
            val = bool(int(user_input))
        else:
            try:
                val = arg_type(user_input)
            except ValueError:
                raise ValueError(f"Invalid input type for '{arg_name}'. Expected a value of type {arg_type.__name__}.")
        return val



def get_methods_map(cls) -> dict[int, callable]:
    public_methods_names = get_methods(cls, public_only=True)
    return {i + 1: getattr(cls, name) for i, name in enumerate(public_methods_names)}


def get_methods(cls, public_only = False) -> list[callable]:
    if public_only:
        attr_filter = lambda attr : callable(getattr(cls, attr)) and not attr.startswith("_")
    else:
        attr_filter = lambda attr : callable(getattr(cls, attr))
    public_methods = [method for method in dir(cls) if attr_filter(method)]
    return public_methods


def get_args(func: callable) -> list[Argument]:
    args = []
    spec = inspect.getfullargspec(func)
    annotations = spec.annotations
    start_index = 1 if spec.args and spec.args[0] in ['self', 'cls'] else 0

    for arg_name in spec.args[start_index:]:
        arg_type = annotations.get(arg_name)
        if arg_type:
            args.append(Argument(dtype=arg_type, name=arg_name))
    return args

#