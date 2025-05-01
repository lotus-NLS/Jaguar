from engine.l0_main.settings import LotusCredentials
from holytools.events import Timer
from tests.basetests import CredTest


# --------------------------------------------

class TestLotusCredentials(CredTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.valid_keys = ['openai_api_key', 'google_api_key', 'search_engine_id', 'enable_introduction']
        cls.invalid_keys = ['invalid_key', 'invalid_key2', 'invalid_key3']

    # --------------------------------------------
    # tests

    def test_creds_work(self):
        creds = LotusCredentials(openai_api_key=self.openai_api_key,google_api_key=self.google_api_key,search_engine_id=self.searchengine_id)
        creds.validate_openai()
        creds.validate_search_engine()

    @staticmethod
    def measure_startup_time():
        timer = Timer()
        print(f'- Measuring LotusCredentials startup time')
        LotusCredentials.from_file()
        print(f'Setting up credentials took {timer.capture(verbose=False)} seconds')

if __name__ == "__main__":
    TestLotusCredentials.execute_all()
    TestLotusCredentials.measure_startup_time()
