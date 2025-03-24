from engine.l2_models.language import Context
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

if __name__ == "__main__":
    TestContext.execute_all()