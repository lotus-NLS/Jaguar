from api import Entry, Speaker, Role
from engine.l2_models.generation import GenerationContext, Options, ToolOptions
import threading
import asyncio

from test_suite.l2.openai_test import OpenAITest
from test_suite.l2.spoof import Greet, NotifyChef
# ---------------------------------------------------------


class TestOpenAIText(OpenAITest):
    @classmethod
    def setup(cls):
        cls.introduction_request = Entry(Speaker.get_user(),msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        cls.repetition_request = Entry(Speaker.get_user(),msg='Can you please repeat what I said above in its entirety?')

    def test_chunk_text(self):
        context = GenerationContext(entries=[self.introduction_request], docs=[])
        generation = self.model.get_generation(context, self.default_options)
        self.log_result(context, generation)

    def test_text_stream(self):
        context = GenerationContext(entries=[self.introduction_request], docs=[])
        generation = self.model.get_generation(context, self.default_options)

        def exhaust():
            for chunk in generation:
                _ = chunk.get_text()

        threading.Thread(target=exhaust).start()
        async def print_stream():
            async for text in generation.get_text_stream():
                self.lineprinter.add(msg=text)

        asyncio.run(print_stream())


class TestOpenAIFunctionCall(OpenAITest):
    @classmethod
    def setup(cls):
        cls.greet_tool = Greet()
        cls.welcome_request = Entry(Speaker(role=Role.USER), msg='##Automated message: Please greet our eight guests and welcome them to our home !')
        cls.chef_notification_request = Entry(Speaker(role=Role.USER), msg='Also please notify the chef that we need food for eight people')

        application_name = 'display'
        cls.greet_tool_docs = Greet().get_json_doc(application_name=application_name)
        cls.notify_chef_docs = NotifyChef().get_json_doc(application_name=application_name)
        cls.tool_allowed_options = Options(tool_options=ToolOptions(call_allowed=True))


    def test_simple_tool_call(self):
        context = GenerationContext(entries=[self.welcome_request], docs=[self.greet_tool_docs])
        generation = self.model.get_generation(context, self.tool_allowed_options)
        self.log_result(context, generation)

    def test_multi_tool_call(self):
        context = GenerationContext(entries=[self.welcome_request], docs=[self.greet_tool_docs, self.notify_chef_docs])
        generation = self.model.get_generation(context, self.tool_allowed_options)
        self.log_result(context, generation)
    #
    def test_text_and_function_call(self):
        talk_request = Entry(Speaker(role=Role.USER), msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')
        context = GenerationContext(entries=[self.welcome_request,talk_request], docs=[self.greet_tool_docs])
        generation = self.model.get_generation(context, self.tool_allowed_options)
        self.log_result(context=context,generation=generation)
    #
    # def test_remembers_tool_output(self):
    #     context = GenerationContext(entries=[self.greet_request, self.repetition], docs=[self.greet_tool_docs])
    #     generation = self.model.get_generation(context, self.tool_allowed_options)
    #     self._print_generation_chunks(generation)


if __name__ == '__main__':
    text_tests = TestOpenAIText()
    text_tests.setup()
    text_tests.execute_all()
