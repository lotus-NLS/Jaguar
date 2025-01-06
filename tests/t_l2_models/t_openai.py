from engine.l2_models.generation import Context
from tests.t_l2_models.openai_test import OpenAITest


# ---------------------------------------------------------

class TestContextOpenAI(OpenAITest):
    def test_text_chunks(self):
        context = Context(entries=[self.mock_entries.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.text_only)
        self.get_result(context, generation)

    def test_text_stream(self):
        context = Context(entries=[self.mock_entries.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.text_only)

        for chunk in generation:
            self.lineprinter.add(msg=chunk.get_text())

    def test_image_context(self):
        context = Context(entries=[self.mock_entries.image_entry], docs=[])
        generation = self.default_model.get_generation(context, self.text_only)
        self.get_result(context, generation)


class TestToolCallOpenAI(OpenAITest):
    def test_simple_tool_call(self):
        context = Context(entries=[self.mock_entries.welcome_request],
                          docs=[self.doc_spoof.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        self.get_result(context, generation)

    def test_multi_tool_call(self):
        context = Context(entries=[self.mock_entries.welcome_request,self.mock_entries.chef_notification_request],
                          docs=[self.doc_spoof.greet_tool_docs, self.doc_spoof.notify_chef_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        text, callMap = self.get_result(context, generation)

        self.assertTrue(len(callMap.values()) == 2)

    def test_text_and_function_call(self):
        context = Context(entries=[self.mock_entries.welcome_request, self.mock_entries.write_text_entries_request],
                          docs=[self.doc_spoof.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed)
        text, callmap = self.get_result(context=context, generation=generation)

        self.assertTrue(text)
        self.assertTrue(len(callmap.values()) == 1)


if __name__ == '__main__':
    TestContextOpenAI.execute_all()
    TestToolCallOpenAI.execute_all()
