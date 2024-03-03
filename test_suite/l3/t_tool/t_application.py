import json

from engine.l3_applications.tool import  Application, OpenTool, ActionTool
from engine.l3_applications.tool.input import ToolArg, ToolCall
from engine.l3_applications.tool.output import Window, WindowMap

from hollarek.devtools import Unittest


class TextWindow(Window):
    def __init__(self, name: str, content: str = ''):
        super().__init__(name)
        self.content = content

    def update(self, new_content: str):
        self.content += new_content

    def get_context(self) -> str:
        return self.content

class SimpleOpenTool(OpenTool):
    def __init__(self, window_map: WindowMap):
        super().__init__(window_map=window_map)

    def get_window(self) -> Window:
        return TextWindow(name='SimpleTextWindow')

    def get_desc(self) -> str:
        return 'Opens a new text window'




class SimpleWriteTool(ActionTool):
    def __init__(self, window_map: WindowMap):
        super().__init__(window_map=window_map, call_timeout=1)
        self.text_arg: ToolArg = ToolArg(name='Text', desc='Text to write')

    def do(self):
        window = self.get_window()
        if window:
            window.update(self.text_arg.val)
        else:
            raise ValueError('Window does not exist')

    @classmethod
    def get_desc(cls) -> str:
        return 'Writes text to a specified window'


class TextApplication(Application):
    @classmethod
    def get_desc(cls):
        return 'A simple text application'

    def create_open_tool(self) -> SimpleOpenTool:
        return SimpleOpenTool(window_map=self.window_map)

    def create_action_tools(self) -> list[ActionTool]:
        return [SimpleWriteTool(window_map=self.window_map)]



class ApplicationTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.app = TextApplication()
        open_window_json_str = json.dumps({})
        cls.open_window_call = ToolCall(json_str=open_window_json_str)

        write_hi_json_str = json.dumps({f"Text": "Hello, TextApplication!", f'window_index' : '0'})
        cls.write_tool_call = ToolCall(json_str=write_hi_json_str)

    def test_open_window(self):
        initial_window_count = len(self.app.window_map)
        self.app.open_tool.handle(tool_call=self.open_window_call)
        self.assertEqual(len(self.app.window_map), initial_window_count + 1, "OpenTool should add a new window")


    def test_write_window(self):
        print(f'Open windows on application count : {len(self.app.window_map)}')
        write_tool = self.app.action_tools[0]
        print(f'Open windows on write tool count : {len(write_tool.window_map)}')
        write_tool.handle(self.write_tool_call)
        target_window = write_tool.get_window()
        print(f'target window context : {target_window.get_context()}')
        self.assertEqual(target_window.get_context(), 'Hello, TextApplication!', "WriteTool should update the window content")


if __name__ == '__main__':
    ApplicationTest.execute_all()