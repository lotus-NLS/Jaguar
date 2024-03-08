from abc import abstractmethod
from api import Entry, Speaker, Role


class Window:
    def __init__(self, index : int, name : str):
        self.tabs: Tabs = Tabs()
        self.index : int = index
        self.name : str = name

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
        basic_info = f'{self.name}; Window number : {self.index}'
        num_dashes = max(header_len - len(basic_info), 0)
        dashes = '=' * num_dashes
        return  f'{dashes} {basic_info} {dashes}'

    def create_entry(self, msg : str) -> Entry:
        return Entry(speaker=Speaker(role=Role.TOOL, name=self.name), msg=msg)


class Tab:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_context(self) -> str:
        pass


class Tabs(dict[int, Tab]):
    pass
