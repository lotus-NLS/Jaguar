import os
from src.l3_agent.tool import Tool,ToolArg
import tempfile
import subprocess

# ---------------------------------------------------------

class RUN(Tool):
    python_script_mode = 0
    cmd_mode = 1

    def __init__(self):
        super().__init__()
        self.description = 'The RUN tool allows you to either run a Python script or execute a command line command as input string'

        self.mode_arg: ToolArg = self.create_arg(name='mode', dtype=int,
                                                 desc=f'I will type either {self.python_script_mode} for python scripts or '
                                                  f'{self.cmd_mode} for command line scripts')

        self.program_content_arg: ToolArg = self.create_arg(name='program_content', dtype=str,
                                                            desc='The content of the Python script or shell command to execute')

    def do(self) -> None:
        mode = self.mode_arg.val

        if not mode in [self.python_script_mode, self.cmd_mode]:
            self.error_log(f'Invalid mode specified. Use "{self.python_script_mode}"'
                           f' for Python script or "{self.cmd_mode}" for command line.')
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
                self.error_log(f'Standard Error:\n{result.stderr}')

        except Exception as e:
            self.error_log(f'An error occurred while trying to run the Python script: {e}')


    def execute_py(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as temp:
            temp.write(self.program_content_arg.val)
            temp_file_path = temp.name

        # Debug
        print(f'Starting subprocess run')
        result = subprocess.run(['python', temp_file_path], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f'Subprocess run finished')
        os.unlink(temp_file_path)

        return result

    def execute_cmd(self):
        result = subprocess.run(self.program_content_arg.val, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result
