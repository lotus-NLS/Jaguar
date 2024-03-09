import unittest
from engine.l2_os import Tab, Application

class MockTab(Tab):
    def __init__(self, path: str):
        super().__init__(path)

    def add(self, msg: str):
        self.text_content += msg

    def reset(self):
        self.text_content = ''

    def open(self):
        pass  # Implement if necessary for your tests

class TestApplication(unittest.TestCase):

    def setUp(self):
        self.app = Application(index=0, tab_type=MockTab)
