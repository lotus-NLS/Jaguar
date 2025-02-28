from engine.l2_models.language import Context
from engine.l2_models.language import Entry
from holytools.devtools import Unittest
from holytools.fileIO import ExampleFiles
from tests.t_l2.base import OpenAITest

# ----------------------------------------------------------

class TestContext(OpenAITest):
    def test_roundtrip(self):
        context = Context.get_example_context()
        s = context.to_str()
        new_context = Context.from_str(s)
        self.assertEqual(context, new_context)

    def test_text_context(self):
        entries = [self.example_entries.introduction]
        self.get_results(entries=entries, docs=[], options=self.text_only)

    def test_image_context(self):
        entries = [self.example_entries.image_entry]
        self.get_results(entries=entries, docs=[], options=self.text_only)


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
    TestContext.execute_all()
    TestEntry.execute_all()