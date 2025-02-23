import time

from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal, Browser
from holytools.logging import Loggable
from holytools.network import Endpoint
from .settings import LotusCredentials
from ..l1_agents.guidance.tasktracker import Task
from ..l2_models.generation.step import Step


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds = LotusCredentials()
        aos = self._get_default_aos()
        self._agent = self._get_default_agent(aos=aos)
        self.dev_endpoint : Endpoint = Endpoint.make_localhost(port=5000, path=f'/update')

    def work(self, task : Task, max_steps : int):
        work_steps = 0
        for step in self._agent.work(task=task, max_steps=max_steps):
            self.observe_step(step=step)
            work_steps += 1

        print(f'Finished work mode after {work_steps} steps')

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
        try:
            self.dev_endpoint.post(msg=step.get_state().to_str(), secure=False)
        except:
            self.warning(f'Context update endpoint {self.dev_endpoint.get_url(protocol=f"https")} unresponsive')

        return response_text

    # ---------------------------------------------------------------
    # build

    def _get_default_aos(self) -> AOS:
        google_api_key = self._creds.get_google_apikey()
        searchengine_id = self._creds.get_searchengine_id()
        browser = Browser(google_api_key=google_api_key, searchengine_id=searchengine_id)
        terminal = Terminal()
        return AOS(workspaces=[terminal, browser])

    def _get_default_agent(self, aos : AOS):
        model = OpenAIModel.default_model(api_key=self._creds.get_openai_apikey())
        return Agent(model=model, aos=aos)


