from engine.l1_agents import Core
from engine.l2_models.language import Context
from engine.l2_models.language import Entry
from engine.l3_aos import AOS
from holytools.devtools import Unittest
from holytools.fileIO import ExampleFiles

# ----------------------------------------------------------

class TestContext(Unittest):
    def test_roundtrip(self):
        context = self.get_example_context()
        s = context.to_str()
        new_context = Context.from_str(s)
        self.assertEqual(context, new_context)

    @staticmethod
    def get_example_context() -> Context:
        system_entry = Core.GOTO().as_system_entry()
        hello_entry = Entry.user(msg=f'Hello there')
        basic_context = Context(entries=[system_entry, hello_entry])

        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos)
        return aos_context + basic_context


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