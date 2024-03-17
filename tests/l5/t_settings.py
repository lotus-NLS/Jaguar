from engine.l5_singletons import LotusSettings
from hollarek.devtools import Unittest
# --------------------------------------------

class TestLotusSettings(Unittest):
    def setUp(self):
        self.tearDown()

    @classmethod
    def setUpClass(cls):
        cls.valid_keys = ['openai_api_key', 'google_api_key', 'search_engine_id', 'enable_introduction']
        cls.invalid_keys = ['invalid_key', 'invalid_key2', 'invalid_key3']


    # --------------------------------------------
    # tests

    def test_local_valid(self):
        self.is_valid(local=True)

    def test_local_ok(self):
        self.is_ok(local=True)

    def test_remote_ok(self):
        self.is_ok(local=False)

    def test_remote_valid(self):
        self.is_valid(local=False)

    # --------------------------------------------

    def is_ok(self,local : bool = True ):
        settings = LotusSettings(use_local=local)
        for key in self.valid_keys:
            self.assertIsInstance(settings.get(key), str)

    def is_valid(self, local : bool = True):
        settings = LotusSettings(use_local=local)
        x,y = settings.validate_openai(), settings.validate_search_engine()
        for val in [x,y]:
            self.assertTrue(val)

    def tearDown(self):
        LotusSettings().reset_instance()


if __name__ == "__main__":
    TestLotusSettings.execute_all()
