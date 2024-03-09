from engine.l3_models.generation import GenerationContext
import threading
import asyncio

from tests.l3.openai_test import OpenAITest

# ---------------------------------------------------------

class TestContextOpenAI(OpenAITest):
    def test_text_chunks(self):
        context = GenerationContext(entries=[self.entry_spoofs.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.text_options)
        self.get_result(context, generation)

    def test_text_stream(self):
        context = GenerationContext(entries=[self.entry_spoofs.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.text_options)

        def exhaust():
            for chunk in generation:
                _ = chunk.get_text()

        threading.Thread(target=exhaust).start()

        async def print_stream():
            async for text in generation.get_text_stream():
                self.lineprinter.add(msg=text)

        asyncio.run(print_stream())

    def test_image_context(self):
        context = GenerationContext(entries=[self.entry_spoofs.image_entry], docs=[])
        generation = self.vision_model.get_generation(context, self.default_options)
        self.get_result(context, generation)


class TestToolCallOpenAI(OpenAITest):
    def test_simple_tool_call(self):
        context = GenerationContext(entries=[self.entry_spoofs.welcome_request],
                                    docs=[self.doc_spoof.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.default_options)
        self.get_result(context, generation)

    def test_multi_tool_call(self):
        context = GenerationContext(entries=[self.entry_spoofs.welcome_request,
                                             self.entry_spoofs.chef_notification_request],
                                    docs=[self.doc_spoof.greet_tool_docs, self.doc_spoof.notify_chef_docs])
        generation = self.default_model.get_generation(context, self.default_options)
        text, callMap = self.get_result(context, generation)

        self.assertTrue(len(callMap.values()) == 2)

    def test_text_and_function_call(self):
        context = GenerationContext(entries=[self.entry_spoofs.welcome_request, self.entry_spoofs.write_text_entries_request],
                                    docs=[self.doc_spoof.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.default_options)
        text, callmap = self.get_result(context=context, generation=generation)

        self.assertTrue(text)
        self.assertTrue(len(callmap.values()) == 1)


if __name__ == '__main__':
    TestContextOpenAI.execute_all()
    TestToolCallOpenAI.execute_all()
    # function_tests = TestToolCallOpenAI()
    # function_tests.execute_all()
    # from PIL import Image
    #
    # spoofer = Spoofer()
    # test_path = spoofer.lend_png()
    # image = Image.open(test_path)
    # image.show()
