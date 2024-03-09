import unittest
from engine.l2_os import Tab, Application

class MockTab(Tab):
    def __init__(self, path: str):
        super().__init__(path)
        self.text_content = 'Initial'

    def add(self, msg: str):
        self.text_content += ' ' + msg

    def reset(self):
        self.text_content = ''

    def open(self):
        pass  # Implement if necessary for your tests

    def get_context(self, app_name: str) -> str:
        return f'{app_name}: {self.text_content}'
