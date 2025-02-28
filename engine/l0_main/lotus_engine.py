import time
import uuid
from typing import Optional

from engine.l1_agents import Agent, Evaluator, Task
from engine.l2_models import OpenAIModel, Step, StepState
from engine.l3_aos import AOS, Terminal, Browser
from holytools.abstract import Serializable
from holytools.logging import Loggable
from holytools.network import Endpoint
from .dev_monitor import DevMonitor
from .settings import LotusCredentials
from ..l1_agents.guidance.workflow import Workflow
from ..l2_models.generation.step import Report


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        dev_monitor : DevMonitor = DevMonitor.default()
        self.step_endpoint: Endpoint = dev_monitor.step_endpoint
        self.report_endpoint : Endpoint = dev_monitor.report_endpoint

        self.session_uuid: str = self.generate_session_uuid()
        self._creds : LotusCredentials = LotusCredentials.from_file()

        browser = Browser(google_api_key=self._creds.google_api_key,
                          searchengine_id=self._creds.search_engine_id)
        terminal = Terminal()
        aos = AOS(workspaces=[terminal, browser])
        model = OpenAIModel.default_model(api_key=self._creds.openai_api_key)

        self._agent = Agent(aos=aos, model=model)
        self._evalutor : Evaluator = Evaluator(model=model)

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

    # --------------------------------------------------------------
    # routines

    def do_workflow(self, wf : Workflow):
        node = wf.start_node
        self.do_task(task=node.task, max_steps=node.max_steps)

        self._agent.handle()

    def do_task(self, task : Task, max_steps : int, dos : Optional[str] = None):
        states : list[StepState] = []
        for step in self._agent.work(task=task, max_steps=max_steps):
            print()
            state = self.observe_step(step=step)
            states.append(state)
        print(f'Finished work mode after {len(states)} steps')
        if not dos is None:
            self.evalute(final_state=states[-1], dos=dos)


    def evalute(self, final_state : StepState, dos : str):
        summary = final_state.writing
        if summary is None:
            raise ValueError('No summary generated')

        if not final_state.is_final:
            is_successful = False
        else:
            is_successful = self._evalutor.evaluateProperty(msg=summary, prop=dos)
        report = Report(summary=summary, is_successful=is_successful, session_uuid=self.session_uuid)
        self.send(endpoint=self.report_endpoint, obj=report)


    def converse(self, msg : str) -> StepState:
        step = self._agent.converse(msg=msg)
        return self.observe_step(step=step)

    # ---------------------------------------------------------------

    def observe_step(self, step : Step, print_chunks : bool = True) -> StepState:
        for text in step.text_pipe.get_text_stream():
            if print_chunks:
                print(text, end='', flush=True)
                time.sleep(0.05)
        step_state = step.get_state(uuid=self.session_uuid)
        self.send(endpoint=self.step_endpoint, obj=step_state)
        return step_state

    def send(self, endpoint : Endpoint, obj : Serializable):
        try:
            endpoint.post(msg=obj.to_str(), secure=False)
        except:
            self.warning(f'Monitor endpoint {endpoint.get_url(protocol=f"https")} unresponsive')