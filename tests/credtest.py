import os

from engine.l0_main.settings import LotusCredentials
from holytools.devtools import Unittest


class CredentialDependentTest(Unittest):
    @classmethod
    def setUpClass(cls):
        try:
            kwargs = {'openai_api_key': os.environ['DEV_OPENAI_API_KEY'],
                      'google_api_key': os.environ['DEV_GOOGLE_API_KEY'],
                      'search_engine_id': os.environ['DEV_SEARCH_ENGINE_ID']}
            credentials = LotusCredentials(**kwargs)
        except:
            credentials : LotusCredentials = LotusCredentials.from_file()

        cls.searchengine_id : str = credentials.search_engine_id
        cls.google_apikey : str = credentials.google_api_key
        cls.openai_apikey : str = credentials.openai_api_key