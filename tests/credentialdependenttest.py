from engine.l0_engine.settings import LotusCredentials
from holytools.devtools import Unittest


class CredentialDependentTest(Unittest):
    @classmethod
    def setUpClass(cls):
        credentials : LotusCredentials = LotusCredentials()
        cls.searchengine_id = credentials.get_searchengine_id()
        cls.google_apikey = credentials.get_google_apikey()
        cls.openai_apikey = credentials.get_openai_apikey()