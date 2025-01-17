from __future__ import annotations

from api import Entry
from engine.l2_models import Context, Options
from engine.l3_aos.tools import ToolDoc, ToolCall
from tests.t_l2.base import OpenAITest


# ---------------------------------------------------------

class TestContextOpenAI(OpenAITest):
    def test_text_context(self):
        entries = [self.example_entries.introduction]
        self.get_results(entries=entries, docs=[], options=self.text_only)

    def test_image_context(self):
        entries = [self.example_entries.image_entry]
        self.get_results(entries=entries, docs=[], options=self.text_only)


class TestToolCallOpenAI(OpenAITest):
    def test_simple_tool_call(self):
        entries = [self.example_entries.welcome_request]
        docs = [self.greet_tool.get_doc()]
        options = self.tool_allowed
        text, calls = self.get_results(entries=entries, docs=docs, options=options)

        self.assertTrue(len(calls) == 1)


    def test_multi_tool_call(self):
        entries = [self.example_entries.welcome_request, self.example_entries.notify_chef]
        docs = [self.greet_tool.get_doc(), self.noify_chef_tool.get_doc()]
        options = self.tool_allowed
        text, calls = self.get_results(entries=entries, docs=docs, options=options)

        self.assertTrue(len(calls) == 2)

    def test_text_and_function_call(self):
        entries = [self.example_entries.welcome_request, self.example_entries.write_num_guests]
        docs = [self.greet_tool.get_doc()]
        options = self.tool_allowed
        text, calls = self.get_results(entries=entries, docs=docs, options=options)

        self.assertTrue(len(text) > 0)
        self.assertTrue(len(calls) == 1)

    def test_require_call(self):
        entries = [self.example_entries.welcome_request]
        docs = [self.greet_tool.get_doc()]
        options = Options.require_call(tool_name=self.greet_tool.get_name())
        text, calls = self.get_results(entries=entries, docs=docs, options=options)

        self.assertTrue(len(calls) == 1)
        c = calls[0]
        self.assertTrue(c.name == self.greet_tool.get_name())


if __name__ == '__main__':
    # TestToolCallOpenAI.execute_all()
    TestContextOpenAI.execute_all()
