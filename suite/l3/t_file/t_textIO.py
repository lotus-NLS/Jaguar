import json
from engine.l3_applications.tool.input import ToolCall
from engine.l3_applications.file.text_io import TextEditor
import tempfile
from hollarek.devtools import Unittest



class TestTextIO(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.app = TextEditor()

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt')
        self.temp_file.write('Initial content of the file\n')
        self.temp_file.flush()
        self.temp_file.close()

        open_window_json_str = json.dumps({'fpath': self.temp_file.name})
        self.open_window_call = ToolCall(json_str=open_window_json_str)

        self.inserted_content = "Hello, TextApplication!"
        write_hi_json_str = json.dumps({'content to insert': self.inserted_content , 'Line number': '2', 'window_index': '0'})
        self.write_tool_call = ToolCall(json_str=write_hi_json_str)

        self.open_tool = self.app.get_tool_dict(active_only=False)['Read']
        self.write_tool = self.app.get_tool_dict(active_only=False)['Insert']


    def test_open_window(self):
        initial_window_count = len(self.app.window_map)
        self.open_tool.handle(tool_call=self.open_window_call)
        self.assertEqual(len(self.app.window_map), initial_window_count + 1)


    def test_open_window_and_read_content(self):
        self.open_tool.handle(tool_call=self.open_window_call)
        new_window = list(self.app.window_map.values())[0]
        self.assertIn('Initial content of the file', new_window.get_context())


    def test_write_to_window_and_verify_content(self):
        self.open_tool.handle(tool_call=self.open_window_call)
        self.write_tool.handle(tool_call=self.write_tool_call)
        target_window = list(self.app.window_map.values())[0]
        self.assertIn(self.inserted_content,target_window.get_context())

if __name__ == '__main__':
    TestTextIO.execute_all()
