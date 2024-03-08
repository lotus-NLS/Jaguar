from typing import Optional
from abc import abstractmethod
from engine.l4_tools import Tool

from .action import Action
from .window import Window, Tab

# ---------------------------------------------------

class Application:
    def __init__(self, index : int, tab_type : type[Tab]):
        super().__init__()
        self.index = index
        self.tab_type : type[Tab] = tab_type

        self.window : Optional[Window] = None
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
        pass

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
        return self.window is not None

