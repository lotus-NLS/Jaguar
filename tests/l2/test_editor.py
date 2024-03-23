from hollarek.file import File, FileSpoofer
from engine.l2_os import LotusText
from hollarek.devtools import Unittest

# ---------------------------------------------------------

class TestTextTab(Unittest):
    def setUp(self):
        self.test_text : File = FileSpoofer.lend_txt()

    def test_content(self):
        tab = LotusText(filepath=self.test_text.fpath)
        self.log(msg=f'Initial content: \n{tab.get_text()}')

    def test_insert(self):
        tab = LotusText(filepath=self.test_text.fpath)
        new_content = 'Second line \n'
        tab.insert(2, new_content)
        self.assertIn(new_content, tab.get_text())
        self.log(msg=tab.get_text())

    def test_delete_lines(self):
        tab = LotusText(filepath=self.test_text.fpath)
        tab.delete_lines(1, 1)
        with open(self.test_text.fpath, 'r') as f:
            content = f.readlines()
        self.assertEqual(len(content), 1)
        self.log(f'After deleting: \n{tab.get_text()}')



if __name__ == '__main__':
    TestTextTab.execute_all()
