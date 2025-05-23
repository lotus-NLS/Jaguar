import os

from tests.basetests import PythonProjTest


class TestProjectNode(PythonProjTest):
    def test_exclude_directores(self):
        self.root_node.fill_ancestors(desc_map={})
        filetree = self.root_node.get_tree()

        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_describe_dirs(self):
        description_map = {os.path.join(self.proj_dirpath, 'somefile.txt') : 'This is a file'}

        self.root_node.fill_ancestors(desc_map=description_map)
        tree = self.root_node.get_tree()

        print(f'- Described tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt\n\tThis is a file' in tree)

    def test_enumerated_tree(self):
        self.root_node.fill_ancestors(desc_map={})
        tree = self.root_node.get_tree(show_idx=True)
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt | FileID = 2' in tree)


if __name__ == "__main__":
    TestProjectNode.execute_all()