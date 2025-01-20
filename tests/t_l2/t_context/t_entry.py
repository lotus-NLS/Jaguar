from engine.l2_models.context import Entry
from holytools.devtools import Unittest
from holytools.fileIO import ExampleFiles

class TestEntry(Unittest):
    def test_roundtrip(self):
        img_file = ExampleFiles.lend_png()
        img = img_file.read()
        entry = Entry.user(name=f'John', msg='Hello there Jane', image=img)
        s = entry.to_str()
        new_entry = Entry.from_str(json_str=s)
        self.assertEqual(entry,new_entry)

if __name__ == "__main__":
    TestEntry.execute_all()