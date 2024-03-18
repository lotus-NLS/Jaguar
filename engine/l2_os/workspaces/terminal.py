import subprocess
import platform
from subprocess import Popen, PIPE
from typing import Optional
from io import StringIO
from PIL.Image import Image as PILImage

from engine.l2_os import Workspace
# ---------------------------------------------------------


class LotusTerminal(Workspace):
    def __init__(self, uri : str):
        super().__init__(uri=uri)
        self.total_text: str = ''
        self.buffer : StringIO = StringIO()
        self.session: Optional[Popen] = self._get_session()

    def get_text(self) -> str:
        return self.buffer.getvalue()

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_desc(self) -> str:
        return f'This application allows you to execute command in the Terminal'

    # ---------------------------------------------------------
    # actions

    def run(self, command : str) :
        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()

    # ---------------------------------------------------------
    # Setup

    def _get_session(self) -> Optional[Popen]:
        os_type = self._get_os_type()
        if  os_type == 'Linux':
            shell_cmd = '/bin/bash'
        elif os_type == 'Windows':
            shell_cmd = 'cmd.exe'
        else:
            raise ValueError(f'OS type {os_type} not supported')

        shell_session = None
        try:
            shell_session = subprocess.Popen(shell_cmd, stdin=PIPE, stdout=self.buffer, stderr=self.buffer, text=True)
        except Exception as e:
            self.error(f'An exception occured while trying to start terminal session using {shell_cmd}: {e}')

        return shell_session

    @staticmethod
    def _get_os_type() -> str:
        return f'{platform.system()}'


if __name__ == "__main__":
    terminal = LotusTerminal(uri='')
    terminal.run(command=f'echo Hello')