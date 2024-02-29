from __future__ import annotations

import copy
import os
from enum import Enum

from hollarek.io import get_text, TextFileType
from hollarek.io.fsys import FsysNode
from ..application import Tool, ToolArg, Application, Window, ToolCall


# ---------------------------------------------------------

class TextIO(Application):
    def __init__(self):
        super().__init__()
        self.available_tool_map = {tool.get_name() : tool for tool in [Write, Read]}
        self.active_tools_map = copy.copy(self.available_tool_map)


    def handle(self, call : ToolCall):
        call.get_args_dict()


class TextWindow(Window):
    def __init__(self, fpath : str):
        super().__init__(name=os.path.basename(fpath))
        self.fpath : str = fpath

    def get_context(self) -> str:
        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        return ''.join(numbered_lines)



class Mode(Enum):
    WRITE = 'write'
    READ = 'read'

    @classmethod
    def modes_as_str_list(cls) -> list[str]:
        return [cls.WRITE.value, cls.READ.value]


class Edit(Tool):
    def __init__(self, fpath : str):
        super().__init__(call_timeout=5)
        self.fpath : str = fpath
        self.desc = f'Allow for inserting or overwriting individual lins of open text windows'

        self.content_arg : ToolArg = ToolArg(name='content to insert', desc='Content to insert')
        self.line_arg : ToolArg = ToolArg(name='Line number', desc='Line number where content will be inserted')
        self.do_overwrite : ToolArg = ToolArg(name='Overwrite existing lines', choices=['0','1'], is_optional=True)


    def do(self):
        line, content, overwrite = int(self.line_arg.val), self.content_arg.val, bool(self.do_overwrite.val)
        self.do_update(line=line, content=content, overwrite=overwrite)


    def do_update(self, line: int, content: str, overwrite: bool = False):
        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")
        content += '' if content.endswith('\n') else '\n'
        index = line - 1
        if overwrite and 0 < line <= len(lines):
            lines[index] = content
        else:
            lines.insert(index, content)
        with open(self.fpath, 'w') as f:
            f.writelines(lines)


class Write(Tool):
    def __init__(self):
        super().__init__()
        self.desc = f'Writes or overwrites text files with given Content '
        self.content_arg: ToolArg = ToolArg(name='content', desc='(New) content of file')
        self.fpath_arg : ToolArg = ToolArg(name='filepath')

    def do(self):
        fpath = os.path.expanduser(self.fpath_arg.val)
        content = self.content_arg.val
        with open(fpath, 'w') as f:
            f.write(content)
        return f'Wrote content to {fpath}'


class Read(Tool):
    def __init__(self):
        super().__init__()
        self.desc = f'Open plain text or pdfs files'
        self.fpath_arg : ToolArg = ToolArg(name='fpath', desc='Filepath to be read or written to')

    def do(self):
        fpath = os.path.expanduser(self.fpath_arg.val)

        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'There is no file located at given location {fpath}. Aborting ...')

        suffix = FsysNode(path=fpath).get_suffix()
        file_type = TextFileType.PDF if suffix == 'pdf' else TextFileType.PLAINTEXT
        return get_text(fpath=fpath, file_type=file_type)



