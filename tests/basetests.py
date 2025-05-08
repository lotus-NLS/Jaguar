from engine.l0_main.lotus_engine import LotusEngine
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents import Agent
from engine.l1_agents.tasks import Task
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from holytools.devtools import Unittest

# ------------------------------------------------------------

class CredTest(Unittest):
    @classmethod
    def setUpClass(cls):
        credentials : LotusCredentials = LotusCredentials.auto()
        # cls.creds : LotusCredentials = credentials
        cls.searchengine_id : str = credentials.search_engine_id
        cls.google_api_key : str = credentials.google_api_key
        cls.openai_api_key : str = credentials.openai_api_key

class AgentTest(CredTest):
    def setUp(self):
        self.model = OpenAIModel.default_model(api_key=self.openai_api_key)
        self.aos = AOS.full(google_api_key=self.google_api_key, searchengine_id=self.searchengine_id)
        self.agent = Agent(aos=self.aos, model=self.model)
        task_yaml = ('- Test task'
                     '    - Mark this task in the Tracker as completed. It only serves to test the Tracker completion functionality.')
        self.example_task = Task.from_yaml(s=task_yaml)
        self.default_inf_config: InfConfig = InfConfig()


class EngineTest(CredTest):
    def setUp(self):
        self.model : LLM = OpenAIModel.default_model(api_key=self.openai_api_key)
        self.engine : LotusEngine = LotusEngine()
        self.agent : Agent = self.engine.agent
