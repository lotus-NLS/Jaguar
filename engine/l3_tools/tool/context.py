from abc import abstractmethod
from typing import Optional
from uuid import uuid4


class Window:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    def add_content(self, content : str):
        self.content += content

    @abstractmethod
    def close(self):
        pass


class ToolContext:
    def __init__(self):
        self.windows : dict[str, Window] = {}


    @abstractmethod
    def add_window(self, window : Window):
        while True:
            uuid = f'{uuid4()}'[:4]
            if not uuid in self.windows:
                break
        self.windows[uuid] = window


    def get_window(self, uuid : str) -> Optional[Window]:
        return self.windows.get(uuid)
