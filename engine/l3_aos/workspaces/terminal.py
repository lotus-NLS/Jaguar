import os
import platform
import subprocess
import time
from typing import Optional

import libtmux
from PIL.Image import Image as PILImage
from libtmux import Session

from engine.l3_aos.tools import InvalidArgValue
from engine.l3_aos.workspace import Workspace


# ---------------------------------------------------------

class Terminal(Workspace):
    def __init__(self):
        super().__init__()
        self.tmux_session : Optional[Session] = None
        self.tmux_name : str = 'lotus'

    def open(self, workdir_path : str = '~'):
        """Opens a terminal in the specified working directory available only to you"""
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.tmux_session = self._open_session(cwd=cwd)

    def close(self):
        """Close LotusTerminal. The session will not be saved"""
        self.tmux_session = None

    def _open_session(self, cwd : str) -> Session:
        os_type = f'{platform.system()}'
        if  os_type == 'Linux':
            shell_cmd = 'bash'
        else:
            raise ValueError(f'OS type {os_type} not supported')

        try:
            subprocess.Popen(['gnome-terminal', '--', 'tmux', 'new-session', '-s', 'lotus'], cwd=cwd)
            time.sleep(2)
            server = libtmux.Server()
            return server.find_where({"session_name": self.tmux_name})
        except Exception as e:
            self.error(msg=f'An exception occured while trying to start terminal session using executable'
                           f' \"{shell_cmd}\": \"{e}\"')
            err = e
            raise err

    # ---------------------------------------------------------
    # actions

    def run(self, command : str) :
        """Runs a command in the current terminal session"""
        window = self.tmux_session.windows[0]
        pane = window.panes[0]
        pane.send_keys(command)

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        window = self.tmux_session.windows[0]
        pane = window.panes[0]
        pane_content = pane.capture_pane()

        text = ''
        for l in pane_content:
            text += f'{l}\n'
        return text


    @classmethod
    def get_desc(cls) -> str:
        return "A terminal in which you can freely execute commands"

if __name__ == "__main__":
    t = Terminal()
    t.open()
    t.run(command='asdf')
    time.sleep(2)

    print(f'Currently terminal reads {t.get_text()}')

    t.run(command='echo "Hellooo from Python via tmux!"')
    time.sleep(2)
    print(f'Currently terminal reads {t.get_text()}')

