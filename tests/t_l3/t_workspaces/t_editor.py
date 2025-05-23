from engine.l3_aos import PythonIDE
from tree import DecoratedDirectory
import tempfile

from holytools.devtools import Unittest
from holytools.fsys import Directory, FsysManager

import os

# --------------------------------------------------------------


class PythonTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.proj_dirpath : str = tempfile.mktemp()
        os.makedirs(cls.proj_dirpath)
        cls.ide : PythonIDE = PythonIDE()
        cls.ide.open(project_dirpath=cls.proj_dirpath)
        cls.view = cls.ide.view

    def setUp(self):
        self.script_fpath = os.path.join(self.proj_dirpath, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = "print(f'Hello world :)')\na = 2\nb=3"
            f.write(testscript_content)


class TestProjectView(PythonTest):
    def test_open_file(self):
        self.ide.open_file(fileNo=0)
        self.ide.get_text()

        self.ide.open_file(fileNo=1)

    def test_script_display(self):
        file_content = self.ide.view._get_with_lineno(fpath=self.script_fpath)
        excepted_content = ''' 1   | print(f'Hello world :)')
 2   | a = 2
 3   | b=3'''

        print(f'- Initial file content:\n{file_content}')
        print(f'- Expected file content:\n{excepted_content}')
        self.assertEqual(file_content, excepted_content)

    def test_exclude_directores(self):
        manager = FsysManager(root_dirpath=self.proj_dirpath)
        manager.add_tree(tree={'.venv': {}, '__pycache__' : {}, 'somefile.txt' : 'Content'})

        filetree = self.view.get_project_filetree()
        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)


class TestDecoratedDirectory(Unittest):
    num_hard_files = 9
    num_hard_folders = 3
    num_total_dat_files = 5
    num_total_files = num_hard_files+1
    num_total_nodes= num_total_files+num_hard_folders

    def setUp(self):
        self.root_dirpath = tempfile.mkdtemp()
        self.files = ['file1.txt', 'file2.txt']
        self.subdirs = ['.hiddendir','dir1', 'dir2']
        self.subfiles = {'dir1': ['sub1.dat', 'sub2.dat', 'sub3.dat', '.hiddenfile.dat'],
                         'dir2': ['sub1.png', 'sub2.png', 'sub3.png']}

        for d in self.subdirs:
            os.makedirs(os.path.join(self.root_dirpath, d))

        for the_file in self.files:
            open(os.path.join(self.root_dirpath, the_file), 'a').close()  # Create empty files

        for subdir, subfiles in self.subfiles.items():
            subdir_path = os.path.join(self.root_dirpath, subdir)
            for subfile in subfiles:
                open(os.path.join(subdir_path, subfile), 'a').close()

        os.symlink(os.path.join(self.root_dirpath, 'dir1', 'sub1.dat'), os.path.join(self.root_dirpath, 'symlink_sub1.dat'))
        self.root_node = DecoratedDirectory(path=self.root_dirpath)

    def test_get_described_tree(self):
        description_map = {os.path.join(self.root_dirpath, 'file1.txt') : 'This is a file'}
        tree = self.root_node.get_tree(desc_map=description_map)
        print(f'- Described tree:\n{tree}')
        self.assertTrue(f'🗎 file1.txt\n			This is a file' in tree)

    def test_enumerated_tree(self):
        path_to_fileID = {os.path.join(self.root_dirpath, 'file1.txt') : '1'}

        tree = self.root_node.get_tree(path_to_fileID=path_to_fileID)
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 file1.txt | FileID = 1' in tree)


if __name__ == "__main__":
    TestDecoratedDirectory.execute_all()