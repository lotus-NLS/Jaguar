from tests.l2.mock_app import MockTab
from engine.l2_os import Application
from hollarek.devtools import Unittest

class TestApplication(Unittest):

    def setUp(self):
        self.app = Application(index=0, tab_type=MockTab, desc='Test application')

    def test_basic_properties(self):
        self.assertEqual(self.app.get_name(), 'Application')
        self.assertIsInstance(self.app.get_desc(), str)
        self.assertFalse(self.app.is_open())

    def test_open_application(self):
        self.app.open(path='some_path')
        self.assertTrue(self.app.is_open())
        self.assertIsInstance(self.app.window.tab_map[0], MockTab)

    def test_close_application(self):
        self.app.open(path='some_path')
        self.app.close()
        self.assertFalse(self.app.is_open())
        self.assertTrue(len(self.app.window.get_tabs()) == 0)

    def test_close_individual_tabs(self):
        self.app.open(path='tab1')
        self.app.open(path='tab2')
        initial_tab_count = len(self.app.window.tab_map)
        self.app.window.close_tab(0)
        self.assertEqual(len(self.app.window.tab_map), initial_tab_count - 1)

    def test_application_actions(self):
        self.app.open(path='some_path')
        actions = self.app.get_actions()
        self.assertIsInstance(actions, list)  # Check that actions are listed
        self.assertGreater(len(actions), 0)  # Check that there are actions available

if __name__ == '__main__':
    TestApplication.execute_all()
