from __future__ import annotations
import os
from typing import Optional

from hollarek.io import get_text, TextFileType
from hollarek.io.fsys import FsysNode
from ..tool import ToolArg, ToolCall, Application, Window, WindowMap, OpenTool, ActionTool


# ---------------------------------------------------------

class TextIO(Application):
    def __init__(self):
        super().__init__()

    def create_open_tool(self) -> OpenTool:
        return Read(window_map=self.window_map)

    def create_action_tools(self) -> list[ActionTool]:
        return [Insert(window_map=self.window_map)]


class TextWindow(Window):
    def __init__(self, fpath : str):
        super().__init__(name=os.path.basename(fpath))
        self.fpath : str = fpath
        self.content : Optional[str] =None


    def get_context(self) -> str:
        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        return ''.join(numbered_lines)


    def update(self, line: int, content: str):
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")

        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        index = line - 1
        lines.insert(index, content)

        with open(self.fpath, 'w') as f:
            f.writelines(lines)


class Insert(ActionTool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map, call_timeout=5)

        self.content_arg : ToolArg = ToolArg(name='content to insert', desc='Content to insert')
        self.line_arg : ToolArg = ToolArg(name='Line number', desc='Line number where content will be inserted')

    def do(self):
        window = self.get_window()
        window.update(line=int(self.line_arg.val), content=self.content_arg.val)

    def get_desc(self) -> str:
        return f'Allow for inserting or overwriting individual lins of open text windows'


class Read(OpenTool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map)
        self.fpath_arg : ToolArg = ToolArg(name='fpath', desc='Filepath of text file to be opened')


    def get_window(self) -> Window:
        fpath = os.path.expanduser(self.fpath_arg.val)

        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'There is no file located at given location {fpath}. Aborting ...')

        suffix = FsysNode(path=fpath).get_suffix()
        file_type = TextFileType.PDF if suffix == 'pdf' else TextFileType.PLAINTEXT

        new = TextWindow(fpath=fpath)
        new.content = get_text(fpath=fpath, file_type=file_type)
        return new


    def get_desc(self) -> str:
        return f'Open plain text or pdfs files'