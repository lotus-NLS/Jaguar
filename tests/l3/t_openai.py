from api import Speaker, Role, Entry
from engine.l3_models.generation import GenerationContext, Options, ToolOptions
import threading
import asyncio
from hollarek.devtools.spoof import Spoofer
from hollarek.fileIO import ImageIO


from tests.l3.openai_test import OpenAITest
from tests.l3.spoof import Greet, NotifyChef

# ---------------------------------------------------------


class TestContextOpenAI(OpenAITest):
    @classmethod
    def setUpClass(cls):
        cls.introduction_request = Entry(Speaker.get_user(),msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        cls.repetition_request = Entry(Speaker.get_user(),msg='Can you please repeat what I said above in its entirety?')

        fpath = Spoofer.lend_png().fpath
        img_io = ImageIO(fpath=fpath)
        img_content = img_io.read()
        cls.image_Entry = Entry(speaker=Speaker.get_user(), msg = f'Can you describe whats in self image?',
                                            image=img_content)


    def test_text_chunks(self):
        context = GenerationContext(entries=[self.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.default_options)
        self.get_result(context, generation)


    def test_text_stream(self):
        context = GenerationContext(entries=[self.introduction_request], docs=[])
        generation = self.default_model.get_generation(context, self.default_options)

        def exhaust():
            for chunk in generation:
                _ = chunk.get_text()

        threading.Thread(target=exhaust).start()
        async def print_stream():
            async for text in generation.get_text_stream():
                self.lineprinter.add(msg=text)

        asyncio.run(print_stream())

    def test_image_context(self):
        context = GenerationContext(entries=[self.image_Entry], docs=[])
        generation = self.vision_model.get_generation(context, self.vision_options)
        self.get_result(context, generation)



class TestToolCallOpenAI(OpenAITest):
    @classmethod
    def setUpClass(cls):
        cls.greet_tool = Greet()
        cls.welcome_request = Entry(Speaker(role=Role.USER), msg='##Automated message: Please greet our eight guests and welcome them to our home!'
                                                                 'You need only do self once, every guest will see it')
        cls.chef_notification_request = Entry(Speaker(role=Role.USER), msg='Also please notify the chef that we need food for eight people')

        application_name = 'display'
        cls.greet_tool_docs = Greet().get_doc(app_name=application_name)
        cls.notify_chef_docs = NotifyChef().get_doc(app_name=application_name)
        cls.tool_allowed_options = Options(tool_options=ToolOptions(call_allowed=True))


    def test_simple_tool_call(self):
        context = GenerationContext(entries=[self.welcome_request], docs=[self.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed_options)
        self.get_result(context, generation)

    def test_multi_tool_call(self):
        context = GenerationContext(entries=[self.welcome_request, self.chef_notification_request], docs=[self.greet_tool_docs, self.notify_chef_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed_options)
        text, callMap = self.get_result(context, generation)

        self.assertTrue(len(callMap.values()) == 2)

    def test_text_and_function_call(self):
        talk_request = Entry(Speaker(role=Role.USER), msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')
        context = GenerationContext(entries=[self.welcome_request,talk_request], docs=[self.greet_tool_docs])
        generation = self.default_model.get_generation(context, self.tool_allowed_options)
        text, callmap = self.get_result(context=context, generation=generation)

        self.assertTrue(text)
        self.assertTrue(len(callmap.values())== 1)


if __name__ == '__main__':
    text_tests = TestContextOpenAI()
    text_tests.execute_all()
    # function_tests = TestToolCallOpenAI()
    # function_tests.execute_all()
    # from PIL import Image
    #
    # spoofer = Spoofer()
    # test_path = spoofer.lend_png()
    # image = Image.open(test_path)
    # image.show()
