import os
import tempfile
import subprocess
import platform
import threading
import time
from typing import Optional
from subprocess import Popen

from src.l2_lotus_core import Tool,ToolArg

# ---------------------------------------------------------


class RUN(Tool):
    python_script_mode = 'py'
    cmd_mode = 'terminal'

    def __init__(self):
        super().__init__()
        self.description = 'The RUN tool allows you to either run a Python script or execute a command line command as input string.'
        self.mode_arg: ToolArg = self.create_arg(
            name='mode', dtype=str,
            available_options=[RUN.python_script_mode,RUN.cmd_mode],
            desc='')

        self.program_content_arg: ToolArg = self.create_arg(
            name='program_content', dtype=str,
            desc='The content of the Python script or shell command to execute')

        self.shell_history = ''
        self.shell_session = self.get_shell_session()
        for stream in [self.shell_session.stdout, self.shell_session.stderr]:
            threading.Thread(target=self.read_stream, args=(stream,)).start()


    def read_stream(self, stream) -> None:
        for line in iter(stream.readline, ''):
            self.shell_history += line


    @staticmethod
    def get_shell_session() -> Optional[Popen]:
        shell_cmd = 'cmd.exe' if platform.system() == 'Windows' else '/bin/sh'
        try:
            shell_session = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f'[Error]: An exception occured while trying to start terminal session using {shell_cmd}: {e}')
            shell_session = None

        return shell_session

    # --------------------------------------------
    #

    def do(self) -> None:
        mode = self.mode_arg.val

        if not mode in [self.python_script_mode, self.cmd_mode]:
            self.semantic_error(f'Invalid mode specified. Use "{self.python_script_mode} for Python script or "{self.cmd_mode}" for command line.')
            return

        if mode == self.python_script_mode:
            execute = self.execute_py
        else:
            execute = self.execute_cmd

        try:
            execute()


        except Exception as e:
            self.exception_log(f'An exception occured during program execution: {e}')


    def execute_py(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp:
            temp.write(self.program_content_arg.val)
            temp_file_path = temp.name

        result = subprocess.run(['python', temp_file_path], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.unlink(temp_file_path)

        if result.stdout:
            self.progress_log(f'Standard Output:\n{result.stdout}')
        if result.stderr:
            self.exception_log(f'Standard Error:\n{result.stderr}')


    def execute_cmd(self)  -> None:
        if self.shell_session is None:
            self.progress_log(f'No shell executable set. Aborting RUN ...')
            return

        self.shell_session.stdin.write(self.program_content_arg.val + '\n')
        self.shell_session.stdin.flush()

        time.sleep(0.1)
        self.progress_log(f'{self.shell_history}')
