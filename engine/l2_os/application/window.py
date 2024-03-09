from abc import abstractmethod
from api import Entry, Speaker, Role
from PIL.Image import Image as PILImage
from typing import Optional
# from hollarek.fsys import URI

class Tab:
    def __init__(self, path : str):
        uri = URI(path=path)

        self.name : str = uri.get_name()
        self.path : str = uri.get_path()
        self.text_content : str = ''
        self.image_content : Optional[PILImage] = None

    @abstractmethod
    def open(self):
        pass

    def get_context(self, app_name : str) -> Entry:
        kwargs = {}
        if self.image_content:
            kwargs['image'] = self.image_content
        return Entry(speaker=Speaker.get_tool(name=app_name), **kwargs)



class Window:
    def __init__(self, index : int, name : str):
        self.tab_map : dict[int, Tab] = {}
        self.index : int = index
        self.name : str = name

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

    def get_context(self) -> Entry:
        context = self.get_header()
        for index, tab in self.tab_map.items():
            context += f'--- {tab.name} ---'
            context += tab.text_content
        return Entry(speaker=Speaker(role=Role.TOOL, name=self.name), msg=context)

    def get_header(self) -> str:
        header_len = 40
        basic_info = f'{self.name}; Window number : {self.index}'
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