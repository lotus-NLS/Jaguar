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
        self.use_root : bool = True

    def open(self, workdir_path : str = '~/testdir'):
        """Opens a terminal in the specified working directory available only to you"""
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.tmux_session = self._open_session(cwd=cwd)
        self.send(content='clear\n')

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
                conditional_root = "sudo -i" if self.use_root else ""
                command = f'tmux new-session -s lotus -d {conditional_root}'
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

    def send(self, content : str) :
        """Sends content to current terminal session. Can be used to execute commands, answer prompts or write in text file. Commands are only executed if an Enter press (=Newline) is included in the content"""
        window = self.tmux_session.windows[0]
        pane = window.panes[0]


        pane.send_keys(cmd=content, enter=False)

    def press_keys(self, key1 : str, key2 : str):
        """Presses a combinatino of keys at the same time. Use key1 = C, s, M to press Ctrl + [key2], Shift + [key2] and Alt + [key2] respectively. Use key1 = 'E', key2 = '' to press enter"""

        window = self.tmux_session.windows[0]
        pane = window.panes[0]
        if key1 == 'E':
            pane.send_keys('', enter=True)
            return

        if key1 in ['C', 's', 'M']:
            key1 = f'{key1}-'
        pane.send_keys(cmd=key1+key2, enter=False)

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

    while True:
        user_input = input()
        if user_input == 'exit':
            break
        t.send(user_input)

    with open('/home/daniel/testdir/example.txt', 'r') as f:
        fcontent = f.read()
        print(f'"{fcontent}"')
