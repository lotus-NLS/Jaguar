from __future__ import annotations
import os
from typing import Optional

from hollarek.fileIO.text import TextIO
from hollarek.fsys import FsysNode
from engine.l4_tools import ToolArg
from engine.l2_os.application import Application, OpeningTool, Action
from engine.l2_os import Tab, Tabs


# ---------------------------------------------------------

class TextEditor(Application):
    def __init__(self):
        super().__init__()

    @classmethod
    def get_desc(cls):
        return f'Allow for opening text files (plain text/pdf) and editing plain text files'

    def create_open_tool(self) -> OpeningTool:
        return Read(window_map=self.window)

    def create_actions(self) -> list[Action]:
        return [Insert(tabs=self.window)]


class TextWindow(Tab):
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
        if FsysNode(path=self.fpath).get_suffix() == 'pdf':
            raise ValueError('Cannot edit pdf files')
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")

        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        index = line - 1
        lines.insert(index, content)

        with open(self.fpath, 'w') as f:
            f.writelines(lines)
        print(f'after update, content is: {self.get_context()}')


class Read(OpeningTool):
    def __init__(self, window_map : Tabs):
        super().__init__(window_map=window_map)
        self.fpath_arg : ToolArg = ToolArg(name='fpath', desc='Filepath of text file to be opened')


    def get_window(self) -> Tab:
        fpath = os.path.expanduser(self.fpath_arg.val)

        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'There is no file located at given location {fpath}. Aborting ...')

        new = TextWindow(fpath=fpath)
        new.content = TextIO.read(fpath=fpath)
        return new


    def get_desc(self) -> str:
        return f'Open plain text or pdfs files'


class Insert(Action):
    def __init__(self, tabs : Tabs):
        super().__init__(tabs=tabs, call_timeout=5)
        self.content_arg : ToolArg = ToolArg(name='content', desc='Content to insert')
        self.line_arg : ToolArg = ToolArg(name='Line number', desc='Line number where content will be inserted')

    def do(self):
        window : TextWindow = self.get_window()
        print(f'window : {window}')
        window.update(line=int(self.line_arg.val), content=self.content_arg.val)


    def get_desc(self) -> str:
        return f'Allow for inserting individual lines of text on open text windows'