from engine.l2_os import Tab

class MockTab(Tab):
    def __init__(self, uri: str):
        super().__init__(uri)
        self.text_content = 'Initial'

    def add(self, msg: str):
        self.text_content += ' ' + msg

    def reset(self):
        self.text_content = ''

    def open(self):
        pass  # Implement if necessary for your tests