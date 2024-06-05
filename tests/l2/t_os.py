import json
from engine.l4_tools import Tool, ToolCall
from engine.l2_os import OS, DocumentEditor
from holytools.devtools import Unittest
from api import Entry


class TestOS(Unittest):
    def setUp(self):
        self.os = OS(workspace_types=[DocumentEditor])
        self.text_workspace = self.os.workspace_map.get(0)
        args_dict = {'filepath' :  '/tmp/3d594cd8-1040-4546-a0b2-0242c81045aa.txt'}
        tool_call = ToolCall(json_str=json.dumps(args_dict))
        self.text_workspace.open_action.handle(tool_call)


    def test_context(self):
        context = self.os.get_context()
        self.assertEqual(len(context.docs),3)
        self.assertEqual(len(context.entries),1)
        entry = context.entries[0]
        self.assertIsInstance(obj=entry, cls=Entry)
        self.assertIsInstance(obj=entry.msg, cls=str)
        print(f'Context is : {context.as_str(section_header="Lotus OS")}')


    def test_tools(self):
        tools = self.os.get_tools()
        self.assertTrue(len(tools) == 3)
        for tool in tools:
            self.assertIsInstance(tool, Tool)


if __name__ == '__main__':
    TestOS.execute_all()
