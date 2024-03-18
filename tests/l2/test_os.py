import json
from engine.l4_tools import Tool, ToolCall
from engine.l2_os import OS, LotusText
from hollarek.devtools import Unittest
from hollarek.file import FileSpoofer

class TestOpenClose(Unittest):
    def setUp(self):
        self.test_txt = FileSpoofer.lend_txt()

        self.os_system = OS(workspace_types=[LotusText])
        self.open_tool = self.os_system.open
        self.text_app = self.os_system.app_map[0]
        open_call_dict = { 'application_index' : 0, 'uri' : self.test_txt.fpath}
        open_call = ToolCall(name=self.open_tool.get_name(), json_str=json.dumps(open_call_dict))
        self.open_tool.handle(tool_call=open_call)


    def test_close(self):
        close_tool = self.os_system.close
        close_call_dict = { 'application_index' : 0}
        close_call = ToolCall(name=close_tool.get_name(), json_str=json.dumps(close_call_dict))
        close_tool.handle(tool_call=close_call)
        self.assertFalse(self.text_app.is_open())


    def test_metatools_found(self):
        tool_names = [tool.get_name() for tool in self.os_system.get_tools()]
        self.assertIn('Open', tool_names)
        self.assertIn('Close', tool_names)



class TestTools(Unittest):
    def setUp(self):
        self.test_txt = FileSpoofer.lend_txt()

        self.os_system = OS(workspace_types=[LotusText])
        self.open_tool = self.os_system.open
        self.text_app = self.os_system.app_map[0]
        open_call_dict = {'application_index': 0, 'uri': self.test_txt.fpath}
        open_call = ToolCall(name=self.open_tool.get_name(), json_str=json.dumps(open_call_dict))
        self.open_tool.handle(tool_call=open_call)

    def test_docs(self):
        docs = self.os_system._get_docs()
        self.assertTrue(len(docs) == 4)

        tool_first_names = ['Open', 'Close', f'{LotusText.insert.__name__}', f'{LotusText.delete_lines.__name__}']

        found_full_names = []
        for doc in docs:
            full_name = doc.get_tool_name()
            found_full_names.append(full_name)
            name_found = any([name in full_name for name in tool_first_names])
            self.assertTrue(name_found)
        self.log(f'Full names : {found_full_names}')


    def test_tools(self):
        tools = self.os_system.get_tools()
        self.assertTrue(len(tools) == 4)
        for tool in tools:
            self.assertIsInstance(tool, Tool)

if __name__ == '__main__':
    TestOpenClose.execute_all()
    TestTools.execute_all()

