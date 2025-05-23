import os

from engine.l3_aos.ide.python_editor import PythonEditor
from tests.basetests import PythonProjTest

# --------------------------------------------------------------

class TestIDE(PythonProjTest):
    def test_open_file(self):
        self.ide.open_file(projectFileNo=0)
        file_content = PythonEditor._get_file_with_lineno(fpath=self.script_fpath)
        excepted_content = ''' 1   | print(f'Hello world :)')
 2   | a = 2
 3   | b=3'''

        print(f'- Initial file content:\n{file_content}')
        print(f'- Expected file content:\n{excepted_content}')
        self.assertEqual(file_content, excepted_content)

        text = self.ide.get_text()
        print(f'- Text:\n{text}')
        self.assertTrue('🗎 test.py | FileID = 0' in text)

    def test_run_file(self):
        self.ide.open_file(projectFileNo=0)
        self.ide.run_file(openFileNo=0)
        out1 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out1}')
        self.assertTrue('Hello world :)' in out1)

        self.ide.run_file(openFileNo=0)
        out2 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out2}')
        self.assertTrue('Hello world :)' in out2)

    def test_insert(self):
        self.ide.open_file(projectFileNo=0)
        fpath = self.script_fpath
        new_content = f'import PIL\n'
        self.ide.insert(fileNo=0, after_line=0, content=new_content)

        file_content = PythonEditor._get_file_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | import PIL
 2   | 
 3   | print(f'Hello world :)')
 4   | a = 2
 5   | b=3'''
        print(f'- New file content:\n{file_content}')
        print(f'- Expected file content\n{expected_file_content}')
        self.assertEqual(file_content, expected_file_content)

    def test_replace(self):
        self.ide.open_file(projectFileNo=0)
        fpath = self.script_fpath
        self.ide.replace(fileNo=0, start_line=1, end_line=1, content='')

        file_content = PythonEditor._get_file_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | a = 2
 2   | b=3'''

        print(f'- New file content:\n{file_content}')
        print(f'- Expected content:\n{expected_file_content}')

        self.assertEqual(file_content, expected_file_content)

    def test_venv_exists(self):
        self.assertTrue(not self.ide.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.ide.interpreter_fpath))


if __name__ == "__main__":
    TestIDE.execute_all()