from engine.l4_singletons import Settings
from hollarek.dev import Unittest


class TestLotusSettings(Unittest):
    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        # Setup for valid settings
        cls.valid_settings = Settings(local=True, validate=False)

    def test_local_valid(self):
        self.assertTrue(self.valid_settings.validate_openai_key())
        self.assertTrue(self.valid_settings.validate_search_engine())

    def test_local_ok(self):
        self.assertIsInstance(self.valid_settings.get('openai_api_key'), str)
        self.assertIsInstance(self.valid_settings.get('google_api_key'), str)
        self.assertIsInstance(self.valid_settings.get('search_engine_id'), str)
        self.assertIsInstance(self.valid_settings.get('enable_introduction'), str)

    # def test_remote_ok(self):
    #     self.assertIsInstance(self.valid_remote_settings.get('openai_api_key'), str)
    #     self.assertIsInstance(self.valid_remote_settings.get('google_api_key'), str)
    #     self.assertIsInstance(self.valid_remote_settings.get('search_engine_id'), str)
    #     self.assertIsInstance(self.valid_remote_settings.get('enable_introduction'), str)


if __name__ == "__main__":
    TestLotusSettings().execute_all()
    # settings = LotusSettings()
    # settings.get('openai_api_key')
