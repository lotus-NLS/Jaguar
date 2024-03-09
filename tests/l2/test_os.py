from engine.l4_tools import Tool
from engine.l2_os import OS, TextWorkspace
from hollarek.devtools import Unittest


class TestOS(Unittest):
    def setUp(self):
        self.temp_file = 'temp_test_file.txt'
        # with open(self.temp_file, 'w') as f:
        #     f.writelines(['Line1\n', 'Line2\n', 'Line3\n'])

        self.os_system = OS(workspace_types=[TextWorkspace])
        self.os_system.app_map.open(uri=self.temp_file)

    def test_tools(self):
        tools = self.os_system.get_tools()
        self.assertTrue(len(tools) == 4)
        for tool in tools:
            self.assertIsInstance(tool, Tool)

    def test_metatools(self):
        tool_map = self.os_system.get_tool_map()
        self.assertIn('Open', tool_map)
        self.assertIn('Close', tool_map)


if __name__ == '__main__':
    TestOS.execute_all()
