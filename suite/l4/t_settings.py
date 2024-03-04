from engine.l4_singletons import Settings
from hollarek.devtools import Unittest
# --------------------------------------------


class TestLotusSettings(Unittest):
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        cls.settings = Settings(local=True, validate=False)
        cls.valid_keys = ['openai_api_key', 'google_api_key', 'search_engine_id', 'enable_introduction']
        cls.invalid_keys = ['invalid_key', 'invalid_key2', 'invalid_key3']

    # --------------------------------------------
    # tests

    def test_local_valid(self):
        self.is_valid(settings=self.settings)

    def test_local_ok(self):
        self.is_ok(settings=self.settings)

    def test_remote_ok(self):
        self.is_ok(settings=self.get_remote_settings())

    def test_remote_valid(self):
        self.is_valid(settings=self.get_remote_settings())

    # --------------------------------------------

    @staticmethod
    def get_remote_settings():
        Settings.reset_instance()
        Settings.configs.reset_instance()
        return Settings(local=False, validate=False)

    def get(self, key : str):
        return self.settings.get(key)

    def is_ok(self, settings : Settings):
        for key in self.valid_keys:
            self.assertIsInstance(settings.get(key), str)

    def is_valid(self, settings : Settings):
        x,y = settings.validate_openai_key(), settings.validate_search_engine()
        for val in [x,y]:
            self.assertTrue(val)

if __name__ == "__main__":
    TestLotusSettings().execute_all()