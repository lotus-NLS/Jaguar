import os

from engine.l0_main.lotus_engine import LotusEngine
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents import Agent
from engine.l2_models import OpenAIModel
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from holytools.devtools import Unittest

# ------------------------------------------------------------

class CredTest(Unittest):
    @classmethod
    def setUpClass(cls):
        credentials : LotusCredentials = LotusCredentials.auto()
        cls.credentials = credentials
        cls.searchengine_id : str = credentials.search_engine_id
        cls.google_apikey : str = credentials.google_api_key
        cls.openai_apikey : str = credentials.openai_api_key

class AgentTest(CredTest):
    def setUp(self):
        model = OpenAIModel.default_model(api_key=self.openai_apikey)
        aos = AOS(workspaces=[])
        self.agent = Agent(aos=aos, model=model)

class EngineTest(CredTest):
    def setUp(self):
        self.model : LLM = OpenAIModel.default_model(api_key=self.openai_apikey)
        self.engine : LotusEngine = LotusEngine()
        self.agent : Agent = self.engine.agent
