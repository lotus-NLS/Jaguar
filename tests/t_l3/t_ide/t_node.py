import os
import tempfile

from engine.l3_aos import PythonIDE
from engine.l3_aos.ide.project_node import ProjectNode
from engine.l3_aos.ide.python_editor import PythonEditor
from holytools.devtools import Unittest
from holytools.fsys import FsysManager
from tests.t_l3.t_ide.t_ide import PythonTest


class TestProjectNode(PythonTest):
    def test_exclude_directores(self):
        self.root_node.fill_ancestors(desc_map={})
        filetree = self.ide._get_project_filetree()

        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_describe_dirs(self):
        description_map = {os.path.join(self.proj_dirpath, 'somefile.txt') : 'This is a file'}

        self.root_node.fill_ancestors(desc_map=description_map)
        tree = self.ide._get_project_filetree()
        print(f'- Described tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt\n\tThis is a file' in tree)

    def test_enumerated_tree(self):
        path_to_fileID = {os.path.join(self.proj_dirpath, 'somefile.txt') : '1'}

        self.ide._populate_project(desc_map={}, path_to_fileID=path_to_fileID)
        tree = self.ide._get_project_filetree()
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt | FileID = 1' in tree)
