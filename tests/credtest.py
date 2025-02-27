import os

from engine.l0_main.settings import LotusCredentials
from holytools.devtools import Unittest


class CredentialDependentTest(Unittest):
    @classmethod
    def setUpClass(cls):
        try:
            kwargs = {'openai_api_key': os.environ['OPENAI_API_KEY'],
                      'google_api_key': os.environ['GOOGLE_API_KEY'],
                      'search_engine_id': os.environ['SEARCHq_ENGINE_ID']}
            credentials = LotusCredentials(**kwargs)
        except KeyError as e:
            print(f'Error: {e.__repr__()}. Falling back to credentials file')
            credentials : LotusCredentials = LotusCredentials.from_file()

        cls.searchengine_id : str = credentials.search_engine_id
        cls.google_apikey : str = credentials.google_api_key
        cls.openai_apikey : str = credentials.openai_api_key