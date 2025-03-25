from engine.l3_aos import Terminal
from engine.l3_aos.tools import ToolCall
from holytools.devtools import Unittest


# ----------------------------------------------------------------

class TerminalText(Unittest):
    def setUp(self):
        self.terminal : Terminal = Terminal()

    def test_get_text(self):
        tc = ToolCall.from_dict(attr_dict={'workdir_path' : '~'})
        self.terminal.open_action._set_args(tool_call=tc)
        self.terminal.open_action.do()
        text = self.terminal.get_text()
        self.assertTrue('@' in text)

    def test_hello_world(self):
        self.terminal.open_action.do()
        echo_text = 'Hello World'
        self.terminal.type(content=f'echo "{echo_text}"')
        text = self.terminal.get_text()
        self.assertTrue(echo_text in text)

if __name__ == "__main__":
    TerminalText.execute_all()