from typing import Optional
from abc import ABC, abstractmethod

class Tool(ABC):
    def __init__(self):
        self.name = None
        self.is_enabled = None

    @abstractmethod
    def handle_call(self, args_dict) -> None:
        pass

    @abstractmethod
    def get_json_doc(self) -> dict:
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def create_arg(self, name: str, dtype: type, desc: str, available_options : Optional[list[str]] = None):
        pass
