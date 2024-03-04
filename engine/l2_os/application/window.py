from abc import abstractmethod

class Window:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_context(self) -> str:
        pass


class WindowMap(dict[int, Window]):
    pass

