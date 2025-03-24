from engine.l2_models.language import Entry
from holytools.devtools import Unittest
from holytools.fileIO import ExampleFiles

# ----------------------------------------------------------

class TestEntry(Unittest):
    def test_roundtrip(self):
        img_file = ExampleFiles.lend_png()
        img = img_file.read()
        e1 = Entry.user(name=f'John', msg='Hello there Jane', image=img)
        e2 = Entry.user(name=f'John', msg='Hello there Jane')

        for entry in [e1, e2]:
            self.assert_roundtrip_equality(entry=entry)

    def assert_roundtrip_equality(self, entry : Entry):
        s = entry.to_str()
        new_entry = Entry.from_str(json_str=s)
        self.assertEqual(entry,new_entry)


if __name__ == "__main__":
    TestEntry.execute_all()