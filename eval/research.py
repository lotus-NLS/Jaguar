from engine.l0_engine.settings import LotusCredentials
from engine.l2_models.llm import LLM
from holytools.devtools import Unittest
from engine.l2_models import OpenAIModel

class SemanticUnittest(Unittest):
    def setUpClass(cls):
        configs = LotusCredentials(use_local=)
        cls.model : LLM = OpenAIModel(api_key=)