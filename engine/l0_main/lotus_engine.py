import time

from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, Terminal, Browser
from holytools.logging import Loggable
from .settings import LotusCredentials
from ..l2_models.generation.pipe import TextPipe


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds = LotusCredentials()
        aos = self._get_default_aos()
        self._agent = self._get_default_agent(aos=aos)

    # def converse(self):
    #     while True:
    #         user_input = input('User: ')
    #         if user_input == 'exit':
    #             break
    #
    #         user_entry = Entry.user(msg=user_input)
    #         self._agent.update_memory(user_entry)
    #         self._agent.handle(step=Step.converse())

    @staticmethod
    def observe_response(response : TextPipe):
        for text in response.get_text_stream():
            print(text, end='', flush=True)
            time.sleep(0.05)

    # ---------------------------------------------------------------

    def _get_default_aos(self) -> AOS:
        google_api_key = self._creds.get_google_apikey()
        searchengine_id = self._creds.get_searchengine_id()
        browser = Browser(google_api_key=google_api_key, searchengine_id=searchengine_id)
        terminal = Terminal()
        return AOS(workspaces=[browser, terminal])

    def _get_default_agent(self, aos : AOS):
        model = OpenAIModel.default_model(api_key=self._creds.get_openai_apikey())
        return Agent(model=model, aos=aos)
