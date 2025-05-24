import json
import os
import tempfile
import time

from engine.l0_main.lotus_engine import LotusEngine
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents import Agent
from engine.l1_agents.tasks import Task
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos import PythonIDE
from engine.l3_aos.ide.project_node import ProjectNode
from engine.l3_aos.tools import ToolCall, Tool, ToolArg
from holytools.devtools import Unittest
from holytools.fsys import FsysManager

# ------------------------------------------------------------

class CredTest(Unittest):
    @classmethod
    def setUpClass(cls):
        credentials : LotusCredentials = LotusCredentials.auto()
        cls.searchengine_id : str = credentials.search_engine_id
        cls.google_api_key : str = credentials.google_api_key
        cls.openai_api_key : str = credentials.openai_api_key

class AgentTest(CredTest):
    def setUp(self):
        self.model = OpenAIModel.default_model(api_key=self.openai_api_key)
        self.aos = AOS.full(google_api_key=self.google_api_key, searchengine_id=self.searchengine_id)
        self.agent : Agent = Agent(aos=self.aos, model=self.model)
        task_yaml = ('- Test task'
                     '    - Mark this task in the Tracker as completed. It only serves to test the Tracker completion functionality.')
        self.example_task = Task.from_yaml(s=task_yaml)
        self.default_inf_config: InfConfig = InfConfig()

class EngineTest(CredTest):
    def setUp(self):
        self.model : LLM = OpenAIModel.default_model(api_key=self.openai_api_key)
        self.engine : LotusEngine = LotusEngine()
        self.agent : Agent = self.engine.agent


class PythonProjTest(Unittest):
    def setUp(self):
        self.proj_dirpath : str = tempfile.mkdtemp()
        self.script_fpath = os.path.join(self.proj_dirpath, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = ""
            f.write(testscript_content)

        fsys_tree = {'__pycache__': {},
                     'somefile.txt': 'Content',
                     'test.py': "print(f'Hello world :)')\na = 2\nb=3",
                     'subdir':
                         {'file1': 'Content', 'file2': 'Content2'}}

        manager = FsysManager(root_dirpath=self.proj_dirpath)
        manager.add_tree(tree=fsys_tree)

        self.ide: PythonIDE = PythonIDE()
        self.ide.open(project_dirpath=self.proj_dirpath)
        self.root_node: ProjectNode = self.ide.root_node


class ToolTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.valid_tool_call : ToolCall = ToolCall(args_json=MockToolCalls.valid_printer_args)
        cls.invalid_tool_call : ToolCall = ToolCall(args_json=MockToolCalls.invalid_printer_args)
        cls.empty_tool_call : ToolCall = ToolCall(args_json=MockToolCalls.empty_args_json)

    def setUp(self):
        self.simple_tool : Tool = PrinterTool()
        self.invalid_tool : Tool = InvalidTool()


class MockToolCalls:
    valid_printer_args = json.dumps({f'arg_one': 'value'})
    invalid_printer_args = json.dumps({'arg_onee': ''})
    empty_args_json = json.dumps({})


class InvalidTool(Tool):
    def get_desc(self) -> str:
        return 'throws error on execution'

    def _do(self):
        raise ValueError

    def get_args(self) -> list[ToolArg]:
        return []


class PrinterTool(Tool):
    def __init__(self, call_timeout: float = 60):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="arg_one")
        self.text_arg_two : ToolArg = ToolArg(name="arg_two", is_optional=True)

    def _do(self):
        time.sleep(0.1)
        msg = f"SimpleTool says: {self.text_arg.input}"
        print(msg)
        return msg

    def get_desc(self) -> str:
        return "SimpleTool is a basic implementation for testing."

    def get_args(self) -> list[ToolArg]:
        return [self.text_arg, self.text_arg_two]