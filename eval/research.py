from engine.l0_engine.settings import LotusCredentials
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool
from holytools.devtools import Unittest
from engine.l2_models import OpenAIModel

class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.

    def do(self):
        pass

    def get_desc(self) -> str:
        pass


class SemanticUnittest(Unittest):
    @classmethod
    def setUpClass(cls):
        configs = LotusCredentials()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.get_openai_apikey())

    def assertProperty(self, msg : str, propety : str):

