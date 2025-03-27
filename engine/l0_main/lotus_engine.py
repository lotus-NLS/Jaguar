import time
import uuid
from typing import Optional

from engine.l1_agents import Agent, Evaluator, Task
from engine.l2_models import OpenAIModel, Step, State, InfConfig
from engine.l3_aos import AOS, Terminal, Browser
from holytools.abstract import Serializable
from holytools.logging import Loggable
from holytools.network import Endpoint
from .dev_monitor import DevMonitor
from .settings import LotusCredentials
from ..l1_agents.guidance.workflow import Workflow
from ..l2_models.generation.step import Report
from ..l2_models.language import Entry
from ..l3_aos.workspaces.python_ide import PythonIDE


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        dev_monitor : DevMonitor = DevMonitor.default()
        self.step_endpoint: Endpoint = dev_monitor.step_endpoint
        self.report_endpoint : Endpoint = dev_monitor.report_endpoint

        self.sess_uuid: str = self.generate_session_uuid()
        self._creds : LotusCredentials = LotusCredentials.from_file()

        browser = Browser(google_api_key=self._creds.google_api_key,
                          searchengine_id=self._creds.search_engine_id)
        terminal = Terminal()
        ide = PythonIDE()
        aos = AOS(workspaces=[terminal, browser, ide])
        model = OpenAIModel.default_model(api_key=self._creds.openai_api_key)

        self.agent = Agent(aos=aos, model=model)
        self._evalutor : Evaluator = Evaluator(model=model)

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

    # --------------------------------------------------------------
    # work

    def do_workflow(self, wf : Workflow):
        node = wf.start_node
        outgoing_edges = wf.outgoing_edge_map[node.name]

        workflow_description = Entry.system(msg=wf.notice)
        self.agent.update_memory(entry=workflow_description)

        while True:
            input(f'Press enter to continue')
            self.do_task(task=node.task, max_steps=node.max_steps)

            exit_tool = wf.get_exit_tool(node_name=node.name)
            self.agent.handle(inf_config=InfConfig(required_tool=exit_tool))

            choice = exit_tool.exit_choice.get_value()
            node = outgoing_edges[choice].target
            if not node.name in wf.outgoing_edge_map:
                break

        self.agent.handle()

    def do_task(self, task : Task, max_steps : int, dos : Optional[str] = None):
        states : list[State] = []
        for step in self.agent.work(task=task, max_steps=max_steps):
            print()
            state = self.observe_step(step=step)
            states.append(state)
        print(f'Finished work mode after {len(states)} steps')
        if not dos is None:
            self.evalute_report(report=states[-1].msg, dos=dos)


    # --------------------------------------------------------------
    # conversation

    def converse(self):
        while True:
            print('User: ', end='')
            user_input = input()
            if user_input == 'exit':
                break

            step = self.agent.talk(msg=user_input)
            self.observe_step(step=step)

            print()

    # ---------------------------------------------------------------

    def evalute_report(self, report : str, dos : str):
        if not report:
            raise ValueError('No summary generated')

        is_successful = self._evalutor.evaluateProperty(report=report, prop=dos)
        report = Report(summary=report, is_successful=is_successful, sess_uuid=self.sess_uuid)
        self.send(endpoint=self.report_endpoint, obj=report)

    def observe_step(self, step : Step, print_chunks : bool = True) -> State:
        step_state = step.get_state(uuid=self.sess_uuid)
        self.send(endpoint=self.step_endpoint, obj=step_state)
        print(f'Agent: ', end='')

        msg = ''
        for chunk in step.text_pipe.get_text_stream():
            msg += chunk
            if print_chunks:
                print(chunk, end='', flush=True)
                time.sleep(0.05)
        step_state.msg = msg

        print()
        return step_state

    def send(self, endpoint : Endpoint, obj : Serializable):
        try:
            endpoint.post(msg=obj.to_str(), secure=False)
        except:
            self.warning(f'Monitor endpoint {endpoint.get_url(protocol=f"https")} unresponsive')
