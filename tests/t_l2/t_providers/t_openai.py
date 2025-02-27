from __future__ import annotations

from engine.l2_models import InfOptions
from tests.t_l2.base import OpenAITest


# ---------------------------------------------------------

class TestContextOpenAI(OpenAITest):
    def test_text_context(self):
        entries = [self.example_entries.introduction]
        self.get_results(entries=entries, docs=[], options=self.text_only)

    def test_image_context(self):
        entries = [self.example_entries.image_entry]
        self.get_results(entries=entries, docs=[], options=self.text_only)




if __name__ == '__main__':
    # TestToolCallOpenAI.execute_all()
    TestContextOpenAI.execute_all()
