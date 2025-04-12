import os
import platform
import subprocess
import time
from typing import Optional

import libtmux
from PIL.Image import Image as PILImage
from libtmux import Session

from engine.l3_aos.tools import InvalidArgValue
from engine.l3_aos.workspaces.workspace import Workspace

# ---------------------------------------------------------

class Terminal(Workspace):
    """A terminal in which you can freely interact with and execute commands in"""
    def __init__(self):
        super().__init__()
        self.tmux_session : Optional[Session] = None
        self.tmux_name : str = 'lotus'

    def open(self, workdir_path : str = '~/testdir'):
        """Opens a terminal in the specified working directory available only to you"""
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.tmux_session = self._open_session(cwd=cwd)
        self.type(content='clear')

    def close(self):
        """Closes the terminal"""
        self.tmux_session = None

    def _open_session(self, cwd : str) -> Session:
        os_type = f'{platform.system()}'
        if  os_type == 'Linux':
            shell_cmd = 'bash'
        else:
            raise ValueError(f'OS type {os_type} not supported')

        try:
            server = libtmux.Server()
            session = server.find_where({"session_name": self.tmux_name})
            if session is None:
                command = 'tmux new-session -s lotus -d'
                subprocess.Popen(['bash', '-c', command], cwd=cwd)
                time.sleep(2)
                session = server.find_where({"session_name": self.tmux_name})
            return session
        except Exception as e:
            self.error(msg=f'An exception occured while trying to start terminal session using executable'
                           f' \"{shell_cmd}\": \"{e}\"')
            err = e
            raise err

    # ---------------------------------------------------------
    # actions

    def type(self, content : str) :
        """Types in current terminal session. Can be used to execute commands, answer prompts or write in text file. Use C-[key], s-[key], M-[key] to press Ctrl+[key], Shift+[key] and Alt+[key] respectively"""
        window = self.tmux_session.windows[0]
        pane = window.panes[0]
        parts = content.split('\n')
        for p in [p for p in  parts if not len(p) == 0]:
            pane.send_keys(p, enter=False)
            pane.enter()

    # ---------------------------------------------------------
    # language

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        window = self.tmux_session.windows[0]
        pane = window.panes[0]
        pane_content = pane.capture_pane(start=-10000)

        text = '\n'.join(pane_content)
        return text


if __name__ == "__main__":
    t = Terminal()
    t.open_action.execute({})

    t.type(content='echo Hellomydude')
    t1 = t.get_text()
    print(f'\nAfter typing:\n{t1}\n')

    t.close_action.execute({})
    t.open_action.execute({})
    t2 = t.get_text()
    print(f'\nAfter re-opening:\n{t2}')