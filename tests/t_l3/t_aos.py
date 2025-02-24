# import json
#
# from engine.l2_models.language import Context, Entry
# from engine.l3_aos import AOS
# from engine.l3_aos.tools import ToolCall, Tool
# from holytools.devtools import Unittest
# # --------------------------------------------------
#
#
# class TestAOS(Unittest):
#     def setUp(self):
#         self.os = AOS(workspaces=[TextEditor()])
#         self.text_workspace = self.os.get_workspaces()[0]
#         args_dict = {'filepath' :  '/tmp/3d594cd8-1040-4546-a0b2-0242c81045aa.txt'}
#         tool_call = ToolCall(json_str=json.dumps(args_dict))
#         self.text_workspace.open_action.execute(tool_call)
#
#     def test_context(self):
#         language = Context.from_aos(aos=self.os)
#         self.assertEqual(len(language.docs),4)
#         self.assertEqual(len(language.entries),1)
#         entry = language.entries[0]
#         self.assertIsInstance(obj=entry, cls=Entry)
#         self.assertIsInstance(obj=entry.msg, cls=str)
#         print(f'Context is : {language.get_view(section_header="Lotus OS")}')
#
#     def test_tools(self):
#         tools = self.os.get_tools()
#         self.assertTrue(len(tools) == 4)
#         for tool in tools:
#             self.assertIsInstance(tool, Tool)
#
#
# if __name__ == '__main__':
#     TestAOS.execute_all()
