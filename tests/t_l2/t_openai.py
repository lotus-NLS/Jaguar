from __future__ import annotations

from engine.l2_models.generation import Context
from tests.t_l2.base import OpenAITest


# ---------------------------------------------------------

class TestContextOpenAI(OpenAITest):
    def test_text_chunks(self):
        context = Context(entries=[self.example_entries.introduction],
                          docs=[])
        generation = self.default_model.get_generation(context, self.text_only)
        self.get_action(context, generation)

    def test_text_stream(self):
        context = Context(entries=[self.example_entries.introduction],
                          docs=[])
        generation = self.default_model.get_generation(context, self.text_only)

        for chunk in generation:
            self.textbox.add(msg=chunk.get_text())

    def test_image_context(self):
        context = Context(entries=[self.example_entries.image_entry],
                          docs=[])
        generation = self.default_model.get_generation(context, self.text_only)
        self.get_action(context, generation)


class TestToolCallOpenAI(OpenAITest):
    def test_simple_tool_call(self):
        context = Context(entries=[self.example_entries.welcome_request],
                          docs=[self.greet_tool.get_doc()])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        self.get_action(context, generation)

    def test_multi_tool_call(self):
        context = Context(entries=[self.example_entries.welcome_request, self.example_entries.notify_chef],
                          docs=[self.greet_tool.get_doc(), self.noify_chef_tool.get_doc()])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        text, callMap = self.get_action(context, generation)

        self.assertTrue(len(callMap.values()) == 2)

    def test_text_and_function_call(self):
        context = Context(entries=[self.example_entries.welcome_request, self.example_entries.write_num_guests],
                          docs=[self.greet_tool.get_doc()])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        text, callmap = self.get_action(context=context, generation=generation)

        self.assertTrue(text)
        self.assertTrue(len(callmap.values()) == 1)


if __name__ == '__main__':
    TestContextOpenAI.execute_all()
    TestToolCallOpenAI.execute_all()
