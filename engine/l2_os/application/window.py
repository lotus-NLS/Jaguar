from abc import abstractmethod

from api import Entry, Speaker, Role
from engine.l2_os.application.actions import Tabs, Tab


class Window:
    def __init__(self, name : str):
        self.tabs: Tabs = Tabs()
        self.name : str = name

    @abstractmethod
    def open(self, uri : str):
        pass

    def get_tabs(self) -> list[Tab]:
        return list(self.tabs.values())

    def get_context(self) -> Entry:
        context = self.get_header()
        for index, tab in self.tabs.items():
            context += f'--- {tab.name} ---'
            context += tab.content
        return self.create_entry(msg=context)


    def get_header(self) -> str:
        header_len = 40
        name = self.__class__.__name__
        num_dashes = max(header_len - len(name), 0)
        dashes = '=' * num_dashes
        return  f'{dashes} {name} {dashes}'

    def create_entry(self, msg : str) -> Entry:
        return Entry(speaker=Speaker(role=Role.TOOL, name=self.name), msg=msg)
