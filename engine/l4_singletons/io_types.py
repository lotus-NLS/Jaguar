from abc import ABC, abstractmethod
from typing import Iterator

from api import Entry


class TextStream(ABC, Iterator[str]):
    @abstractmethod
    def __iter__(self) -> 'TextStream':
        pass

    @abstractmethod
    def __next__(self) -> str:
        pass

    @abstractmethod
    def send(self, value):
        pass

    @abstractmethod
    def throw(self, typ, val=None, tb=None):
        pass

    @abstractmethod
    def close(self):
        pass


class Query:
    @abstractmethod
    def get_confirmation(self) -> bool:
        pass

    def get_text(self) -> str:
        pass


class Server:
    @abstractmethod
    def get_response(self, entry : Entry) -> TextStream:
        pass
