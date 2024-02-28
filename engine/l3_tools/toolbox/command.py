import logging
import subprocess
import platform
import threading

from subprocess import Popen, STDOUT, PIPE
from threading import Lock
from typing import Optional

from hollarek.events import Countdown
from engine.l3_tools.tool import Tool, ToolArg
# ---------------------------------------------------------

class Command(Tool):
    os_in_use = platform.system()

    def __init__(self):
        super().__init__()
        self.desc = f'Run commands in the terminal'
        self.cmd_arg: ToolArg = ToolArg(name='program_content', dtype=str,desc='The code to execute')
        self.shell = Shell()


    def do(self):
        try:
            self.shell.execute_command(command=self.cmd_arg.val)
            self.content += self.shell.get_buffer()

        except Exception as e:
            raise RuntimeError(f'An exception occured during program execution: {e}')


class Shell:
    def __init__(self):
        self.session : Optional[Popen] = self.get_session()
        self.history : list[str] = []
        self.history_lock = Lock()

        self.log_countdown = Countdown(time_to_finish=0.25)
        self.buffer_str : str = ''

        threading.Thread(target=self.listen_stdout).start()

    # ---------------------------------------------------------
    # Setup

    @staticmethod
    def get_session() -> Optional[Popen]:
        shell_cmd = 'cmd.exe' if Command.os_in_use == 'Windows' else '/bin/bash'
        shell_session = None
        try:
            shell_session = subprocess.Popen(shell_cmd,stdin=PIPE, stdout=PIPE,stderr=STDOUT, text=True)

        except Exception as e:
            logging.error(f'An exception occured while trying to start terminal session using {shell_cmd}: {e}')

        return shell_session


    def listen_stdout(self):
        while True:
            line = self.session.stdout.readline()
            self.update_history(line)

    # ---------------------------------------------------------
    # Routine

    def execute_command(self, command : str) :
        if self.session is None:
            raise ValueError(f'No shell executable set. Aborting RUN ...')

        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()

        self.session.stdin.write("echo 'cmd_done'\n")
        self.session.stdin.flush()

        self.log_countdown.launch()


    def update_history(self, msg : str):
        with self.history_lock:
            self.history.append(msg)
            self.buffer_str += msg
            self.log_countdown.relaunch()


    def get_buffer(self) -> str:
        self.log_countdown.finish()
        temp, self.buffer_str = self.buffer_str, ''
        return temp
