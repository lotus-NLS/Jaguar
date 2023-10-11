from typing import Callable
from abc import ABC, abstractmethod
from typing import Optional, Type, Any, List, Dict


from src.l2_lotus_agent.m2_tool_interface.tool_arg import ToolArg
# ---------------------------------------------------------


class ToolInterface(ABC):

    def __init__(self):
        self.name: str = self.__class__.__name__
        self.desc: str = ''
        self.external_log: Callable = lambda *args, **kwargs: None
        self.arg_dict: dict[str, ToolArg] = {}
        self.is_enabled: bool = True

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def create_arg(self, name: str, dtype: Type, desc: str, available_options: Optional[List[str]] = None,
                   is_optional: bool = False) -> Any:  # Replace Any with ToolArg when defined
        pass

    @abstractmethod
    def handle_call(self, args_dict: Dict[str, Any]):
        pass

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_json_doc(self) -> Dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def get_is_json_serializable(json_obj: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def reset_args(self):
        pass

    @abstractmethod
    def get_arg_list(self) -> List[Any]:  # Replace Any with ToolArg when defined
        pass

    @abstractmethod
    def get_required_args_list(self) -> List[Any]:  # Replace Any with ToolArg when defined
        pass