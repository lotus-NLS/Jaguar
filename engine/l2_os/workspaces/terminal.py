import os, fcntl
import subprocess
import platform
from subprocess import Popen, PIPE
from typing import Optional
from func_timeout import func_timeout, FunctionTimedOut
from PIL.Image import Image as PILImage
from engine.l4_tools import InvalidArgValue
import socket

from .workspace import Workspace
# ---------------------------------------------------------

class LotusTerminal(Workspace):
    def __init__(self):
        super().__init__()
        self.near_end, self.far_end = os.pipe()
        fcntl.fcntl(self.near_end, fcntl.F_SETFL, os.O_NONBLOCK)
        self.session: Optional[Popen] = None
        self.content = ''

    def open(self, workdir_path : str = '~'):
        print(f'cwd, workdirpath = {workdir_path}')
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.session = self._get_session(cwd=cwd)

    def close(self):
        self.session = None
        self.content = None

    def _get_session(self, cwd : str) -> Optional[Popen]:
        os_type = self._get_os_type()
        if  os_type == 'Linux':
            shell_cmd = '/bin/bash'
        # elif os_type == 'Windows':
        #     shell_cmd = 'cmd.exe'
        # Also needs adjustments in current directory printing
        else:
            raise ValueError(f'OS type {os_type} not supported')

        shell_session = None
        try:
            out = self.far_end
            shell_session = subprocess.Popen(shell_cmd, stdin=PIPE, stdout=out, stderr=out, text=True, cwd=cwd)
        except Exception as e:
            self.error(f'An exception occured while trying to start terminal session using {shell_cmd}: {e}')

        return shell_session

    # ---------------------------------------------------------
    # actions

    def run(self, command : str) :
        user = 'agent'
        hostname = socket.gethostname()
        self.session.stdin.write(f'echo "{user}@{hostname}:$(pwd)$ "')
        self.session.stdin.flush()

        self.session.stdin.write(command+ '\n')
        self.session.stdin.flush()

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        if self.session is None:
            return ''
        try:
            func_timeout(func=self._read_pipe,timeout=0.25)
        except FunctionTimedOut:
            self.error(f'Function _read_pipe timed out')


        return self.content


    def _read_pipe(self):
        try:
            while True:
                self.content += f'{os.read(self.near_end, 1024).decode()}\n'
        except BlockingIOError:
            pass




    @staticmethod
    def _get_os_type() -> str:
        return f'{platform.system()}'

#