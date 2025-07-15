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
        node_to_idx = self.root_node.get_node_to_idx()

        tree = self.root_node.get_tree(node_to_idx=node_to_idx)
        print(f'- Enumerated tree:\n{tree}')
        self.assertIn(f'🗎 somefile.txt | ID = 1', tree)

    def test_get_tree(self):
        actual_tree = self.root_node.get_tree()
        expected_tree = f'''🗀 {os.path.basename(self.proj_dirpath)}/
	🗎 somefile.txt
	🗎 test.py
	🗀 subdir/
		🗎 file1
		🗎 file2'''

        print(f'- Filetree:\n{actual_tree}')
        self.assertEqual(actual_tree, expected_tree)

    def test_parenthood(self):
        decendants = self.root_node.get_descendants()
        last_desc = decendants[-1]
        self.assertIs(last_desc.parent.parent, self.root_node)

if __name__ == "__main__":
    TestSourceNode.execute_all()