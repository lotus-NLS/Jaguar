from engine.l2_models.language import Message
from holytools.devtools import Unittest
from holytools.fileIO import ExampleFiles

# ----------------------------------------------------------

class TestEntry(Unittest):
    def test_roundtrip(self):
        img_file = ExampleFiles.lend_png()
        img = img_file.read()
        e1 = Message.user(name=f'John', text='Hello there Jane', image=img)
        e2 = Message.user(name=f'John', text='Hello there Jane')

        for entry in [e1, e2]:
            self.assert_roundtrip_equality(entry=entry)

    def assert_roundtrip_equality(self, entry : Message):
        s = entry.to_str()
        new_entry = Message.from_str(json_str=s)
        self.assertEqual(entry,new_entry)


if __name__ == "__main__":
    TestEntry.execute_all()