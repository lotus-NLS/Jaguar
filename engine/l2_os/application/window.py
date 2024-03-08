from abc import abstractmethod
from api import Entry, Speaker, Role


class Tab:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_context(self, app_name : str) -> Entry:
        pass


class Window:
    def __init__(self, index : int, name : str):
        self.tabs : dict[int, Tab] = {}
        self.index : int = index
        self.name : str = name

    def get_tabs(self) -> list[Tab]:
        return list(self.tabs.values())

    def close_tab(self, index):
        del self.tabs[index]

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

