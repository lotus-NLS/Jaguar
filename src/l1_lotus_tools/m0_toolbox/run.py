import os
import tempfile
import subprocess
import platform
import threading
import queue
import time

from src.l2_lotus_core import Tool,ToolArg

# ---------------------------------------------------------





class CommandResult:
    def __init__(self, stdout='', stderr=''):
        self.stdout = stdout
        self.stderr = stderr

class RUN(Tool):
    python_script_mode = 'py'
    cmd_mode = 'terminal'

    def __init__(self):
        super().__init__()

        shell_cmd = 'cmd.exe' if platform.system() == 'Windows' else '/bin/sh'
        try:
            self.shell_session = subprocess.Popen(shell_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            print(f'[Error]: An exception occured while trying to start terminal session using {shell_cmd}: {e}')
            self.shell_session = None

        self.stdout_q = queue.Queue()
        self.stderr_q = queue.Queue()

        self.stdout_thread = threading.Thread(target=self.reader_thread, args=(self.shell_session.stdout, self.stdout_q))
        self.stderr_thread = threading.Thread(target=self.reader_thread, args=(self.shell_session.stderr, self.stderr_q))

        self.stdout_thread.daemon = True
        self.stderr_thread.daemon = True

        self.stdout_thread.start()
        self.stderr_thread.start()


        self.description = 'The RUN tool allows you to either run a Python script or execute a command line command as input string.'
        self.mode_arg: ToolArg = self.create_arg(
            name='mode', dtype=str,
            available_options=[RUN.python_script_mode,RUN.cmd_mode],
            desc='')
            # desc=f'Type either {self.python_script_mode} for python scripts or {self.cmd_mode} for command line '

        self.program_content_arg: ToolArg = self.create_arg(
            name='program_content', dtype=str,
            desc='The content of the Python script or shell command to execute')

    @staticmethod
    def reader_thread(pipe, q):
        while True:
            line = pipe.readline()
            if line:
                q.put(line)
            else:
                break

    def do(self) -> None:
        mode = self.mode_arg.val

        if not mode in [self.python_script_mode, self.cmd_mode]:
            self.semantic_error(f'Invalid mode specified. Use "{self.python_script_mode} for Python script or "{self.cmd_mode}" for command line.')
            return

        if mode == self.python_script_mode:
            execution_with_return_result = self.execute_py
        else:
            execution_with_return_result = self.execute_cmd

        try:
            result = execution_with_return_result()

            if result.stdout:
                self.progress_log(f'Standard Output:\n{result.stdout}')
            if result.stderr:
                self.exception_log(f'Standard Error:\n{result.stderr}')

        except Exception as e:
            self.exception_log(f'An exception occured during program execution: {e}')


    def execute_py(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp:
            temp.write(self.program_content_arg.val)
            temp_file_path = temp.name

        result = subprocess.run(['python', temp_file_path], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.unlink(temp_file_path)

        return result



    def execute_cmd(self):

        if self.shell_session is None:
            self.progress_log(f'No shell executable set. Aborting RUN ...')
            return

        self.shell_session.stdin.write(self.program_content_arg.val + '\n')
        self.shell_session.stdin.flush()

        time.sleep(0.1)  # Adjust the time as needed

        stdout_data = []
        stderr_data = []

        # Collect stdout
        while not self.stdout_q.empty():
            stdout_data.append(self.stdout_q.get().strip())

        # Collect stderr
        while not self.stderr_q.empty():
            stderr_data.append(self.stderr_q.get().strip())

        return CommandResult(stdout='\n'.join(stdout_data), stderr='\n'.join(stderr_data))


