from abc import abstractmethod
from api import Entry, Speaker, Role
from PIL.Image import Image as PILImage
from typing import Optional
# from hollarek.fsys import URI

class Tab:
    def __init__(self, uri : str):
        uri = URI(path=uri)
        uri_name = uri.get_name()

        self.name : str = uri_name if uri_name else 'unnamed tab'
        self.path : str = uri

    @abstractmethod
    def get_text(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    def get_entry(self, tab_index : int, app_name : str) -> Entry:
        kwargs = {}
        image = self.get_image()
        if image:
            kwargs['image'] = image
        msg = self.get_tab_header(msg=f' Tab {tab_index}: {self.name} ')
        msg += self.get_text()
        msg += self.get_tab_header()

        return Entry(speaker=Speaker.get_tool(name=app_name), msg=msg, **kwargs)

    @staticmethod
    def get_tab_header(msg: str = ''):
        max_tab_len = 20
        num_dashes = max(max_tab_len - len(msg), 0)
        dashes = '-' * int(num_dashes / 2)
        return f'\n{dashes}{msg}{dashes}'


class Window:
    def __init__(self, index : int, app_name : str):
        self.tab_map : dict[int, Tab] = {}
        self.index : int = index
        self.app_name : str = app_name

    def add_tab(self, tab : Tab):
        index = 0
        while self.tab_map.get(index):
            index += 1
        self.tab_map[index] = tab

    def close_all(self):
        self.tab_map = {}

    def close_tab(self, index : int):
        del self.tab_map[index]

    # ---------------------------------------------------
    # do

    def get_tabs(self) -> list[Tab]:
        return list(self.tab_map.values())


    def get_entry(self) -> Entry:
        entry = Entry.tool(name=self.app_name, msg=f'\n{self.get_window_header()}')
        for index, tab in self.tab_map.items():
            tab_entry = tab.get_entry(tab_index=index, app_name=self.app_name)
            entry.join(tab_entry)
        return entry


    def get_window_header(self) -> str:
        header_len = 60
        basic_info = f'Application: \"{self.app_name}\" Window number : {self.index}'
        num_dashes = max(header_len - len(basic_info), 0)
        dashes = '=' * num_dashes
        return  f'{dashes} {basic_info} {dashes}'


from urllib.parse import urlparse
from pathlib import Path

class URI:
    def __init__(self, path: str):
        self.type = None
        self.path = path
        parsed = urlparse(path)
        is_url = parsed.scheme and parsed.netloc
        self.wrapper = parsed if is_url else Path(path)

    def get_path(self) -> str:
        return self.path

    def get_name(self) -> str:
        if isinstance(self.wrapper, Path):
            return self.wrapper.name
        else:
            return self.wrapper.path.split('/')[-1]