import os, fcntl
import subprocess
import platform
import time
from subprocess import Popen, PIPE
from typing import Optional
from func_timeout import func_timeout, FunctionTimedOut
from PIL.Image import Image as PILImage
from engine.l4_tools import InvalidArgValue
import socket
import select
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
        """Opens a terminal in which you can freely execute commands"""
        print(f'cwd, workdirpath = {workdir_path}')
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.session = self._get_session(cwd=cwd)

    def close(self):
        """Close LotusTerminal. The session will not be saved"""
        self.session = None
        self.content = None

    def _get_session(self, cwd : str) -> Optional[Popen]:
        os_type = f'{platform.system()}'
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
        """Runs a command in the current terminal session"""
        user = 'agent'
        hostname = socket.gethostname()
        self.session.stdin.write(f'echo "{user}@{hostname}:$(pwd)$ {command}"; {command}\n')
        self.session.stdin.flush()

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        text = self._get_pipe_content(0.01)
        while text:
            self.content += text
            text = self._get_pipe_content(0.01)
        return self.content


    def _get_pipe_content(self, timeout : float) -> Optional[str]:
        readable, _, _ = select.select([self.near_end], [], [], timeout)
        return os.read(self.near_end, 1024).decode() if readable else None