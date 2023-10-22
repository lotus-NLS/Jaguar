import subprocess
import platform
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from subprocess import Popen
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

        except Exception as e:
            self.exception_log(f'An exception occured during program execution: {e}')


class Shell:
    def __init__(self):
        self.session : Popen = self.get_session()
        self.stdout_stream = iter(self.session.stdout.readline, '')
        self.stderr_stream = iter(self.session.stdout.readline, '')


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


    def execute_command(self, command : str) :
        if self.session is None:
            raise ValueError(f'No shell executable set. Aborting RUN ...')

        self.session.stdin.write(command + '\n')
        self.session.stdin.flush()

        self.session.stdin.write("echo 'cmd_done'\n")
        self.session.stdin.flush()

        self.log_command()


    def log_command(self):
        async def log_first_input():
            executor = ThreadPoolExecutor()
            coroutine_1 = self.print_stream(executor=executor,stream=self.session.stdout)
            coroutine_2 = self.print_stream(executor=executor,stream=self.session.stderr)

            tasks = [asyncio.create_task(coroutine_1), asyncio.create_task(coroutine_2)]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            for task in pending:
                task.cancel()

        asyncio.run(log_first_input())

    @staticmethod
    async def print_stream(executor, stream):
        def do():
            print(stream.readline())

        await asyncio.get_event_loop().run_in_executor(executor,do)