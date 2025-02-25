import time
import uuid

from engine.l1_agents import Agent, Evaluator, Task
from engine.l2_models import OpenAIModel, Step, StepState
from engine.l3_aos import AOS, Terminal, Browser
from holytools.logging import Loggable
from holytools.network import Endpoint
from .settings import LotusCredentials

# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self.dev_endpoint: Endpoint = Endpoint.make_localhost(port=5000, path=f'/update')
        self.session_uuid: str = self.generate_session_uuid()
        self._creds : LotusCredentials = LotusCredentials.from_file()
        self._agent = Agent(aos=self._get_default_aos(), model=self._get_default_model())
        self._evalutor : Evaluator = Evaluator(model=self._get_default_model())

    def work(self, task : Task, max_steps : int, dos : str = ''):
        states : list[StepState] = []
        for s in self._agent.work(task=task, max_steps=max_steps):
            states += [self.observe_step(step=s)]
        print(f'Finished work mode after {len(states)} steps')

        if dos:
            report = states[-1].writing
            if report is None:
                raise ValueError('No report generated')
            self._evalutor.evaluateProperty(msg=report, prop=dos)

    def converse(self, msg : str) -> str:
        step = self._agent.converse(msg=msg)
        return self.observe_step(step=step)

    def observe_step(self, step : Step, print_chunks : bool = True) -> str:
        response_text = ''
        for text in step.text_pipe.get_text_stream():
            response_text += text
            if print_chunks:
                print(text, end='', flush=True)
                time.sleep(0.05)

        writing = response_text if len(response_text) > 0 else None
        step_state = step.get_state(uuid=self.session_uuid, writing=writing)

        try:
            self.dev_endpoint.post(msg=step_state.to_str(), secure=False)
        except:
            self.warning(f'Context update endpoint {self.dev_endpoint.get_url(protocol=f"https")} unresponsive')

        return response_text

    # ---------------------------------------------------------------
    # build

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

    def _get_default_aos(self) -> AOS:
        google_api_key = self._creds.google_api_key
        searchengine_id = self._creds.search_engine_id
        browser = Browser(google_api_key=google_api_key, searchengine_id=searchengine_id)
        terminal = Terminal()
        return AOS(workspaces=[terminal, browser], cautious_mode=True)

    def _get_default_model(self):
        return OpenAIModel.default_model(api_key=self._creds.openai_api_key)


