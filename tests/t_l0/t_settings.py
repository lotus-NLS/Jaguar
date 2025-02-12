from engine.l0_main.settings import LotusCredentials
from holytools.devtools import Unittest
from holytools.events import Timer
# --------------------------------------------

class TestLotusCredentials(Unittest):
    def setUp(self):
        self.credentials = LotusCredentials()

    @classmethod
    def setUpClass(cls):
        cls.valid_keys = ['openai_api_key', 'google_api_key', 'search_engine_id', 'enable_introduction']
        cls.invalid_keys = ['invalid_key', 'invalid_key2', 'invalid_key3']

    # --------------------------------------------
    # tests

    def test_cred_exist(self):
        self.credentials.get_google_apikey()
        self.credentials.get_openai_apikey()
        self.credentials.get_searchengine_id()


    def test_creds_work(self):
        self.credentials.validate_openai()
        self.credentials.validate_search_engine()

    @staticmethod
    def measure_startup_time():
        timer = Timer()
        print(f'- Measuring LotusCredentials startup time')
        LotusCredentials()
        print(f'Setting up credentials took {timer.capture(verbose=False)} seconds')

if __name__ == "__main__":
    # TestLotusCredentials.execute_all()
    TestLotusCredentials.measure_startup_time()
