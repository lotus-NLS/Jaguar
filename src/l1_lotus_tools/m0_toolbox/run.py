import os
import tempfile
import subprocess
import platform
import threading
from typing import Optional
from subprocess import Popen
import time
from src.l2_lotus_agent import ToolArg
from pyutils import InputWaiter

from src.l1_lotus_tools.tool import Tool
# ---------------------------------------------------------


class RUN(Tool):
    python_script_mode = 'py'
    cmd_mode = 'terminal'
    os_in_use = platform.system()

    def __init__(self):
        super().__init__()
        self.desc = f'Run code in chosen mode'

        self.mode_arg: ToolArg = self.create_arg(
            name='mode', dtype=str,
            available_options=[RUN.python_script_mode,RUN.cmd_mode],
            desc='')

        self.program_content_arg: ToolArg = self.create_arg(
            name='program_content', dtype=str,
            desc='The code to execute')

        self.logging_backlog = ''
        self.shell_session = self.get_shell_session()
        self.is_error_state = False
        self.output_collector = InputWaiter()
        self.last_msg_time = time.time()

        thread_list = [threading.Thread(target=self.read_terminal_stderr)
                  ,threading.Thread(target=self.read_terminal_stdout)
                  ,threading.Thread(target=self.log_terminal_when_idle)]

        for thread in thread_list:
            thread.daemon = True
            thread.start()


    def do(self):
        mode = self.mode_arg.val

        if not mode in [self.python_script_mode, self.cmd_mode]:
            self.semantic_error(f'Invalid mode specified. Use "{self.python_script_mode} for Python script or "{self.cmd_mode}" for command line.')
            return

        try:
            self.execute_py() if mode == self.python_script_mode else self.execute_terminal()
            self.output_collector.read()

        except Exception as e:
            self.exception_log(f'An exception occured during program execution: {e}')


    def execute_py(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp:
            temp.write(self.program_content_arg.val)
            temp_file_path = temp.name

        result = subprocess.run(['python', temp_file_path], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.unlink(temp_file_path)

        if result.stdout:
            self.update_log(f'Standard Output:\n{result.stdout}')
        if result.stderr:
            self.exception_log(f'Standard Error:\n{result.stderr}')


    def execute_terminal(self) :
        if self.shell_session is None:
            self.update_log(f'No shell executable set. Aborting RUN ...')
            return

        self.shell_session.stdin.write(self.program_content_arg.val + '\n')
        self.shell_session.stdin.flush()

        self.shell_session.stdin.write("echo 'cmd_done'\n")
        self.shell_session.stdin.flush()

    # --------------------------------------------

    @staticmethod
    def get_shell_session() -> Optional[Popen]:
        shell_cmd = 'powershell' if RUN.os_in_use == 'Windows' else '/bin/sh'
        try:
            shell_session = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f'[Error]: An exception occured while trying to start terminal session using {shell_cmd}: {e}')
            shell_session = None

        return shell_session


    def log_terminal_when_idle(self):
        while True:
            current_time = time.time()
            if self.is_error_state:
                logger = self.exception_log
                flag_str = 'Terminal Standard Error'
            else:
                logger = self.update_log
                flag_str = 'Terminal Standard Output'

            if current_time - self.last_msg_time >= 0.25 and self.logging_backlog != '':
                out_str = f'{flag_str}\n{self.logging_backlog}'
                logger(out_str)
                self.output_collector.write(out_str)
                self.logging_backlog = ''
                self.is_error_state = False
                self.last_msg_time = time.time()

            time.sleep(0.05)


    def read_terminal_stdout(self):
        for line in iter(self.shell_session.stdout.readline, ''):
            cleaned_line = line.strip()
            if cleaned_line != '':
                self.logging_backlog += f'{cleaned_line}'


    def read_terminal_stderr(self):
        for line in iter(self.shell_session.stderr.readline, ''):
            cleaned_line = line.strip()
            if cleaned_line != '':
                self.is_error_state = True
                self.logging_backlog += f'{cleaned_line}'