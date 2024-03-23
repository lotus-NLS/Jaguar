import os, fcntl
import subprocess
import platform
from subprocess import Popen, PIPE
from typing import Optional
from func_timeout import func_timeout, FunctionTimedOut
from PIL.Image import Image as PILImage
from .workspace import Workspace
# ---------------------------------------------------------

class LotusTerminal(Workspace):
    def __init__(self):
        super().__init__()
        self.near_end, self.far_end = os.pipe()
        fcntl.fcntl(self.near_end, fcntl.F_SETFL, os.O_NONBLOCK)
        self.session: Optional[Popen] = None
        self.text = ''

    def open(self, workdir_path : str):
        super().open()
        self._get_session(cwd=workdir_path)

    def get_text(self) -> str:
        try:
            func_timeout(func=self._read_pipe,timeout=0.25)
        except FunctionTimedOut:
            self.error(f'Function _read_pipe timed out')
        return self.text

    def get_image(self) -> Optional[PILImage]:
        return None

    # ---------------------------------------------------------
    # actions

    def run(self, command : str) :
        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()

    # ---------------------------------------------------------
    # Setup

    def _read_pipe(self):
        try:
            while True:
                self.text += os.read(self.near_end, 1024).decode()
        except BlockingIOError:
            pass

    def _get_session(self, cwd : str) -> Optional[Popen]:
        os_type = self._get_os_type()
        if  os_type == 'Linux':
            shell_cmd = '/bin/bash'
        elif os_type == 'Windows':
            shell_cmd = 'cmd.exe'
        else:
            raise ValueError(f'OS type {os_type} not supported')

        shell_session = None
        try:
            out = self.far_end
            if not cwd:
                cwd = '~'
            cwd = os.path.expanduser(cwd)
            shell_session = subprocess.Popen(shell_cmd, stdin=PIPE, stdout=out, stderr=out, text=True, cwd=cwd)
        except Exception as e:
            self.error(f'An exception occured while trying to start terminal session using {shell_cmd}: {e}')

        return shell_session

    @staticmethod
    def _get_os_type() -> str:
        return f'{platform.system()}'

#