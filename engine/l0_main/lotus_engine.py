import time

from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal
from holytools.logging import Loggable
from .settings import LotusCredentials
from ..l1_agents.guidance.tasktracker import Task
from ..l2_models.generation.pipe import TextPipe


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds = LotusCredentials()
        aos = self._get_default_aos()
        self._agent = self._get_default_agent(aos=aos)

    def work(self, mandate : Task, max_steps : int):
        self._agent.work(task=mandate, max_steps=max_steps)

    def converse(self, msg : str) -> str:
        text_pipe = self._agent.converse(msg=msg)
        return self.observe_response(pipe=text_pipe)

    @staticmethod
    def observe_response(pipe : TextPipe, print_chunks : bool = True) -> str:
        response_text = ''
        for text in pipe.get_text_stream():
            response_text += text
            if print_chunks:
                print(text, end='', flush=True)
                time.sleep(0.05)
        return response_text

    # ---------------------------------------------------------------

    def _get_default_aos(self) -> AOS:
        # google_api_key = self._creds.get_google_apikey()
        # searchengine_id = self._creds.get_searchengine_id()
        # browser = Browser(google_api_key=google_api_key, searchengine_id=searchengine_id)
        terminal = Terminal()
        return AOS(workspaces=[terminal])

    def _get_default_agent(self, aos : AOS):
        model = OpenAIModel.default_model(api_key=self._creds.get_openai_apikey())
        return Agent(model=model, aos=aos)
