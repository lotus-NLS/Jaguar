import os

from tests.basetests import PythonProjTest


class TestSourceNode(PythonProjTest):
    def test_exclude_directores(self):
        filetree = self.root_node.get_tree()

        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_enumerated_tree(self):
        tree = self.root_node.get_tree(show_idx=True)
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt | FileID = 0' in tree)

    def test_get_tree(self):
        actual_tree = self.root_node.get_tree()
        expected_tree = f'''🗀 {os.path.basename(self.proj_dirpath)}/
	🗀 subdir/
		🗎 file1
		🗎 file2
	🗎 somefile.txt
	🗎 test.py'''

        print(f'- Filetree:\n{actual_tree}')
        self.assertEqual(actual_tree, expected_tree)


if __name__ == "__main__":
    TestSourceNode.execute_all()