import json
import tempfile
from hollarek.devtools import Unittest

from engine.l2_os.file import TextEditor
from engine.l2_os.file.text_editor import Insert, Read
from engine.l4_tools import ToolCall



class TestTextIO(Unittest):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.app = TextEditor()
        self.open_tool : Read = self.app.get_tool_dict(active_only=False)['Read']
        self.write_tool  : Insert = self.app.get_tool_dict(active_only=False)['Insert']

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt')
        self.temp_file.write('Initial content of the file\n')
        self.temp_file.flush()
        self.temp_file.close()


        open_window_json_str = json.dumps({'fpath': self.temp_file.name})
        self.open_window_call = ToolCall(json_str=open_window_json_str)
        self.inserted_content = "Hello, TextApplication!"

        write_hi_json_str = json.dumps({f'{self.write_tool.content_arg.name}': self.inserted_content, 'Line number': '2', 'window_index': '0'})
        self.write_tool_call = ToolCall(json_str=write_hi_json_str)


    def test_open_window(self):
        initial_window_count = len(self.app.window_map)
        self.open_tool.handle(tool_call=self.open_window_call)
        self.assertEqual(len(self.app.window_map), initial_window_count + 1)


    def test_open_and_read(self):
        self.open_tool.handle(tool_call=self.open_window_call)
        new_window = list(self.app.window_map.values())[0]
        self.assertIn('Initial content of the file', new_window.get_context())


    def test_write(self):
        open_output =self.open_tool.handle(tool_call=self.open_window_call)
        write_output = self.write_tool.handle(tool_call=self.write_tool_call)

        for output in [open_output, write_output]:
            if output.get_error_msgs():
                raise RuntimeError(output.get_error_msgs())

        target_window = list(self.app.window_map.values())[0]
        print(self.app.window_map.values())
        print(target_window.get_context())
        self.assertIn(self.inserted_content,target_window.get_context())

if __name__ == '__main__':
    TestTextIO.execute_all()
