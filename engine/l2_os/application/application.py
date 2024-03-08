from typing import Optional
from abc import abstractmethod
from engine.l4_tools import Tool

from .action import Action
from .window import Window

# ---------------------------------------------------

class Application:
    def __init__(self, index : int):
        super().__init__()
        self.index = index
        self.window : Optional[Window] = None
        self.actions : list[Action] = self.create_actions()
        self.tool_dict : dict[str, Tool] = {tool.get_name() : tool for tool in self.actions}

    @abstractmethod
    def create_actions(self) -> list[Action]:
        pass

    @abstractmethod
    def add_tab(self, uri : Optional[str]):
        pass

    def open(self, uri : Optional[str]):
        if not self.window:
            self.window = Window(index=self.index, name=self.get_name())
        self.add_tab(uri=uri)

    def close(self):
        self.window = None
        self.actions = self.create_actions()

    # ---------------------------------------------------
    #  context

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    @abstractmethod
    def get_desc(cls):
        pass

    def is_open(self) -> bool:
        return self.window is not None

    # ---------------------------------------------------
    # tools

    def get_actions(self, active_only : bool= False) -> list[Action]:
        return [action for action in self.actions if action.is_active or not active_only]