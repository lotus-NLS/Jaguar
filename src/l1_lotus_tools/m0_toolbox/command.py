import subprocess
import platform
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from subprocess import Popen
from pyutils import Countdown
from src.l2_lotus_agent.m0_agent.tool_handler import ToolArg

from src.l1_lotus_tools.m0_toolbox.tool import Tool
# ---------------------------------------------------------


class COMMAND(Tool):
    os_in_use = platform.system()

    def __init__(self):
        super().__init__()
        self.desc = f'Run commands in the terminal'

        self.cmd_arg: ToolArg = self.create_arg(
            name='program_content', dtype=str,
            desc='The code to execute')

        self.logging_backlog = ''
        self.shell = Shell()


    def do(self):
        try:
            self.shell.execute_command(command=self.cmd_arg.val)
            self.update_log(self.shell.read_buffer())

        except Exception as e:
            self.exception_log(f'An exception occured during program execution: {e}')


class Shell:
    def __init__(self):
        self.session : Popen = self.get_session()
        self.stdout_stream = iter(self.session.stdout.readline, '')
        self.stderr_stream = iter(self.session.stdout.readline, '')
        self.history : list[str] = []
        self.finish_countdown = Countdown(time_to_finish=0.25)

        self.buffer = ''

        self.history_lock = Lock()
        self.start_listen()


    @staticmethod
    def get_session() -> Optional[Popen]:
        shell_cmd = 'cmd.exe' if COMMAND.os_in_use == 'Windows' else '/bin/sh'
        try:
            shell_session = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f'[Error]: An exception occured while trying to start terminal session using {shell_cmd}: {e}')
            shell_session = None

        return shell_session


    def read_buffer(self) -> str:
        temp, self.buffer = self.buffer, ''
        return temp


    def update_history(self, msg : str):
        self.history.append(msg)
        self.buffer += msg
        self.finish_countdown.reset()


    def execute_command(self, command : str) :
        if self.session is None:
            raise ValueError(f'No shell executable set. Aborting RUN ...')

        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()

        self.session.stdin.write("echo 'cmd_done'\n")
        self.session.stdin.flush()

        self.finish_countdown.launch()
        self.finish_countdown.get()


    def start_listen(self):
        executor = ThreadPoolExecutor(max_workers=2)
        executor.submit(self.listen_stream, self.session.stdout)
        executor.submit(self.listen_stream, self.session.stderr)


    def listen_stream(self, stream):
        while True:
            line = stream.readline()
            with self.history_lock:
                self.update_history(line)
