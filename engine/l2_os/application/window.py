from __future__ import annotations
from abc import abstractmethod
from PIL.Image import Image as PILImage
from typing import Optional
from api import Entry
from hollarek.devtools import ModuleInspector
from hollarek.core.logging import Loggable
# ---------------------------------------------------------

class Window:
    def __init__(self, index : int, app_name : str):
        self.workspace_map : dict[int, Workspace] = {}
        self.app_name : str = app_name
        self.index : int = index

    def add_workspace(self, tab : Workspace):
        index = 0
        while self.workspace_map.get(index):
            index += 1
        self.workspace_map[index] = tab

    def close_all(self):
        self.workspace_map = {}

    def close_tab(self, index : int):
        del self.workspace_map[index]

    # ---------------------------------------------------
    # do

    def get_tabs(self) -> list[Workspace]:
        return list(self.workspace_map.values())

    def get_entry(self) -> Entry:
        basic_info = f'Application: \"{self.app_name}\" Window number : {self.index}'
        entry = Entry.as_tool(name=f'{self.app_name}', msg=basic_info)
        for index, workspace in self.workspace_map.items():
            entry.add_msg(msg=workspace.get_text())
        return entry



class Workspace(Loggable):
    def __init__(self, uri : str):
        super().__init__()
        self.uri : str = uri

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_desc(self) -> str:
        pass

    @classmethod
    def get_init_argname(cls) -> Optional[str]:
        init_args = ModuleInspector.get_args(cls.__init__)
        name = None
        if init_args:
            name = init_args[0].name
        return name
