from hollarek.devtools import Spoofer
from engine.l2_os import TextTab


import unittest

class TestTextTab(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_file_path = Spoofer.lend_txt().fpath

    def test_insert(self):
        # Test the insert functionality
        tab = TextTab(uri=self.test_file_path)
        tab.insert(2, "New line\n")  # Insert a new line at position 2
        expected_content = ["First line\n", "New line\n", "Second line\n"]
        with open(self.test_file_path, 'r') as f:
            content = f.readlines()
        self.assertEqual(content, expected_content)

    def test_delete_lines(self):
        tab = TextTab(uri=self.test_file_path)
        tab.delete_lines(1, 1)  # Delete the first line
        expected_content = ["Second line\n"]  # Expecting the second line to remain
        with open(self.test_file_path, 'r') as f:
            content = f.readlines()
        self.assertEqual(content, expected_content)


if __name__ == '__main__':
    unittest.main()
