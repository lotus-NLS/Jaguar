import os

from tests.basetests import PythonProjTest


class TestSourceNode(PythonProjTest):
    def test_exclude_directores(self):
        self.root_node.fill_ancestors()
        filetree = self.root_node.get_tree()

        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_enumerated_tree(self):
        self.root_node.fill_ancestors()
        tree = self.root_node.get_tree(show_idx=True)
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt | FileID = 0' in tree)

    def test_get_tree(self):
        self.root_node.fill_ancestors()
        actual_tree = self.root_node.get_tree()
        expected_tree = f'''🗀 {os.path.basename(self.proj_dirpath)}/
	🗎 somefile.txt
	🗎 test.py
	🗀 subdir/
		🗎 file1
		🗎 file2'''

        print(f'- Filetree:\n{actual_tree}')
        self.assertEqual(actual_tree, expected_tree)

    def test_get_pruned(self):
        test_fpath = os.path.join(self.proj_dirpath, 'test.py')
        subdir_dirpath = os.path.join(self.proj_dirpath, 'subdir')
        file2_fpath = os.path.join(subdir_dirpath, 'file2')

        new_node = self.root_node.get_pruned(paths=[test_fpath, subdir_dirpath, file2_fpath])
        actual_tree = new_node.get_tree()
        expected_tree = f'''🗀 {os.path.basename(self.proj_dirpath)}/
	🗎 test.py
	🗀 subdir/
		🗎 file2'''

        print(f'- Pruned filetree:\n{actual_tree}')
        self.assertEqual(actual_tree, expected_tree)


if __name__ == "__main__":
    TestSourceNode.execute_all()