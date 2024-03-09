import json
from engine.l4_tools import Tool, ToolCall
from engine.l2_os import OS, TextWorkspace
from hollarek.devtools import Unittest, FileSpoofer

class TestOS(Unittest):
    def setUp(self):
        self.test_txt = FileSpoofer.lend_txt()

        self.os_system = OS(workspace_types=[TextWorkspace])
        self.open_tool = self.os_system.open
        self.text_app = self.os_system.app_map[0]
        open_call_dict = { 'application_index' : 0, 'uri' : self.test_txt.fpath}
        open_call = ToolCall(name=self.open_tool.get_name(), json_str=json.dumps(open_call_dict))
        self.open_tool.handle(tool_call=open_call)

    def test_tools(self):
        tools = self.os_system.get_tools()
        self.assertTrue(len(tools) == 4)
        for tool in tools:
            self.assertIsInstance(tool, Tool)

    def test_metatools(self):
        tool_map = self.os_system.get_tool_map()
        self.assertIn('Open', tool_map)
        self.assertIn('Close', tool_map)

    def test_docs(self):
        docs = self.os_system.get_docs()
        self.assertTrue(len(docs) == 4)
        tool_names = []
        for doc in docs:
            tool_name = doc.get_tool_name()
            tool_names.append(tool_name)
            self.assertTrue(tool_name in ['Open', 'Close',f'{TextWorkspace.insert.__name__}', f'{TextWorkspace.delete_lines.__name__}'])
        self.log(tool_names)

    def test_close(self):
        close_tool = self.os_system.close
        close_call_dict = { 'application_index' : 0}
        close_call = ToolCall(name=close_tool.get_name(), json_str=json.dumps(close_call_dict))
        close_tool.handle(tool_call=close_call)
        self.assertFalse(self.text_app.is_open())

if __name__ == '__main__':
    TestOS.execute_all()
