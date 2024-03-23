from abc import abstractmethod
from PIL.Image import Image as PILImage
from typing import Optional
from urllib.parse import urlparse
from pathlib import Path
from api import Entry
from hollarek.devtools import ModuleInspector
from hollarek.core.logging import Loggable
# ---------------------------------------------------------

class Workspace(Loggable):
    def __init__(self, uri : str):
        super().__init__()
        self.uri : str = uri

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_image(self) -> Optional[PILImage]:
        pass

    def get_entry(self, tab_index : int, app_name : str) -> Entry:
        kwargs = {}
        image = self.get_image()
        if image:
            kwargs['image'] = image
        msg = self._get_workspace_header(msg=f' Tab {tab_index}: {self.uri} ')
        msg += self.get_text()
        msg += self._get_workspace_header()

        return Entry.as_tool(msg=msg, name=app_name, **kwargs)

    @staticmethod
    def _get_workspace_header(msg: str = ''):
        max_len = 50
        num_dashes = max(max_len - len(msg), 0)
        dashes = '-' * int(num_dashes / 2)
        return f'\n{dashes}{msg}{dashes}'

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_desc(self) -> str:
        pass

    @classmethod
    def get_init_argname(cls) -> Optional[str]:
        init_args = ModuleInspector.get_args(cls.__init__)
        name = None
        if init_args:
            name = init_args[0].name
        return name


class Window:
    def __init__(self, index : int, app_name : str):
        self.workspace_map : dict[int, Workspace] = {}
        self.app_name : str = app_name
        self.index : int = index

    def add_workspace(self, tab : Workspace):
        index = 0
        while self.workspace_map.get(index):
            index += 1
        self.workspace_map[index] = tab

    def close_all(self):
        self.workspace_map = {}

    def close_tab(self, index : int):
        del self.workspace_map[index]

    # ---------------------------------------------------
    # do

    def get_tabs(self) -> list[Workspace]:
        return list(self.workspace_map.values())


    def get_entry(self) -> Entry:
        entry = Entry.as_tool(name=self.app_name, msg=f'\n{self.get_window_header()}')
        for index, tab in self.workspace_map.items():
            tab_entry = tab.get_entry(tab_index=index, app_name=self.app_name)
            entry += tab_entry
        return entry


    def get_window_header(self) -> str:
        header_len = 60
        basic_info = f'Application: \"{self.app_name}\" Window number : {self.index}'
        num_dashes = max(header_len - len(basic_info), 0)
        dashes = '=' * num_dashes
        return  f'{dashes} {basic_info} {dashes}'


class URI:
    def __init__(self, path: str):
        super().__init__()
        parsed = urlparse(path)
        is_url = bool(parsed.scheme and parsed.netloc)
        self.type = 'URL' if is_url else 'Path'
        self.path = path
        self.wrapper = parsed if is_url else Path(path)

    def get_path(self) -> str:
        return self.path

    def get_name(self) -> str:
        if isinstance(self.wrapper, Path):
            return self.wrapper.name
        else:
            return self.wrapper.path.split('/')[-1] if self.wrapper.path else ''


if __name__ == "__main__":
    print(URI('C:\\Users\\User\\Documents\\report.txt').get_name())