from engine.l1_agents import Identity
from engine.l2_models.language import Context, Entry
from engine.l3_aos import AOS
from holytools.devtools import Unittest

class TestContext(Unittest):
    def test_roundtrip(self):
        context = self.get_example_context()
        s = context.to_str()
        new_context = Context.from_str(s)
        self.assertEqual(context, new_context)

    @staticmethod
    def get_example_context() -> Context:
        system_entry = Identity.GOTO().as_system_entry()
        hello_entry = Entry.user(msg=f'Hello there')
        basic_context = Context(entries=[system_entry, hello_entry])

        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos, with_update=False)
        return aos_context + basic_context

if __name__ == "__main__":
    TestContext.execute_all()