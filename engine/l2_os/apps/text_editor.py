from __future__ import annotations
import os
from typing import Optional
from api import Entry, Speaker

from hollarek.fileIO.text import TextIO
from hollarek.fsys import FsysNode

from engine.l2_os import Window
from engine.l4_tools import ToolArg
from engine.l2_os.application import Application, Action, Tab


# ---------------------------------------------------------

class TextEditor(Application):
    def create_window(self, uri: str) -> Window:
        return Window(index=self.index, name=self.get_name())

    @classmethod
    def get_desc(self):
        return f'Allow for opening text files (plain text/pdf) and editing plain text files'

    def create_actions(self) -> list[Action]:
        return []


# class TextTab(Tab):
#     def __init__(self, fpath : str):
#         super().__init__(name=os.path.basename(fpath))
#         self.fpath : str = fpath
#         self.content : Optional[str] =None


    # def get_context(self, app_name : str) -> Entry:
    #     with open(self.fpath, 'r') as f:
    #         lines = f.readlines()
    #     numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
    #     msg = ''.join(numbered_lines)
    #     entry = Entry(speaker=Speaker.get_tool(name=app_name), msg=msg)
    #     return entry


    # def update(self, line: int, content: str):
    #     if FsysNode(path=self.fpath).get_suffix() == 'pdf':
    #         raise ValueError('Cannot edit pdf files')
    #     if line <= 0:
    #         raise ValueError("Line number must be a positive integer.")
    #
    #     with open(self.fpath, 'r') as f:
    #         lines = f.readlines()
    #     index = line - 1
    #     lines.insert(index, content)
    #
    #     with open(self.fpath, 'w') as f:
    #         f.writelines(lines)
    #     print(f'after update, content is: {self.get_context()}')

#
# class Read(Action):
#     fpath = 'fpath'
#
#     @classmethod
#     def create_args(cls) -> list[ToolArg]:
#         return [ToolArg(name=cls.fpath, desc='Path to file')]
#
#     def do(self):
#         fpath = os.path.expanduser(self.get_arg_val(name=self.fpath))
#
#         if not os.path.isfile(fpath):
#             raise FileNotFoundError(f'There is no file located at given location {fpath}. Aborting ...')
#
#         new = TextWindow(fpath=fpath)
#         new.content = TextIO.read(fpath=fpath)
#         return new
#
#     def get_desc(self) -> str:
#         return f'Open any text file including plain text and pdf files'

#
# class Insert(Action):
#     def __init__(self, tabs : Tabs):
#         super().__init__(tabs=tabs, call_timeout=5)
#         self.content_arg : ToolArg = ToolArg(name='content', desc='Content to insert')
#         self.line_arg : ToolArg = ToolArg(name='Line number', desc='Line number where content will be inserted')
#
#     def do(self):
#         window : TextWindow = self.get_window()
#         print(f'window : {window}')
#         window.update(line=int(self.line_arg.val), content=self.content_arg.val)
#
#
#     def get_desc(self) -> str:
#         return f'Allow for inserting individual lines of text on open text windows'