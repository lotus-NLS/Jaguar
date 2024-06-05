from engine.l5_settings import LotusSettings
from holytools.devtools import Unittest
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
        LotusSettings.set_configs(use_local=local, enable_validation=False)
        for key in self.valid_keys:
            self.assertIsInstance(LotusSettings.get(key), str)

    def is_valid(self, local : bool = True):
        LotusSettings.set_configs(use_local=local, enable_validation=True)
        x,y = LotusSettings.validate_openai(), LotusSettings.validate_search_engine()
        for val in [x,y]:
            self.assertTrue(val)

    def tearDown(self):
        LotusSettings.reset()


if __name__ == "__main__":
    TestLotusSettings.execute_all()
