import logging
import subprocess
import platform
import threading

from subprocess import Popen, STDOUT, PIPE
from threading import Lock
from typing import Optional

from hollarek.events import Countdown
from engine.l3_applications.tool import Tool, ToolArg
from io import StringIO
# ---------------------------------------------------------

class Command(Tool):
    os_in_use = platform.system()

    def __init__(self):
        super().__init__()
        self.desc = f'Run commands in the terminal'
        self.cmd: ToolArg = ToolArg(name='program_content', desc='The code to execute')
        self.shell = Shell()


    def do(self):
        try:
            self.shell.execute_command(command=self.cmd.val)
            self.___content_depr___ += self.shell.get_buffer()

        except Exception as e:
            raise RuntimeError(f'An exception occured during program execution: {e}')


class Shell:
    def __init__(self):
        self.session : Optional[Popen] = self.get_session()
        self.log_countdown = Countdown(time_to_finish=0.25)
        self.buffer : StringIO = StringIO()

    # ---------------------------------------------------------
    # Setup

    def get_session(self) -> Optional[Popen]:
        shell_cmd = 'cmd.exe' if Command.os_in_use == 'Windows' else '/bin/bash'
        shell_session = None
        try:
            shell_session = subprocess.Popen(shell_cmd, stdin=PIPE, stdout=self.buffer,
                                             stderr=self.buffer.buffer, text=True)
        except Exception as e:
            logging.error(f'An exception occured while trying to start terminal session using {shell_cmd}: {e}')

        return shell_session

    # ---------------------------------------------------------
    # Routine

    def execute_command(self, command : str) :
        if self.session is None:
            raise ValueError(f'No shell executable set. Aborting RUN ...')

        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()
        self.log_countdown.launch()


    def get_buffer(self) -> str:
        self.log_countdown.finish()
        return self.buffer.getvalue()


