
from hollarek.devtools import Unittest
from api import Entry, Speaker, Role
from engine.l3_applications.tool import ToolArg, Tool, ToolCall
from engine.l2_models.generation import GenerationContext, Options, ToolOptions, Generation
from engine.l2_models.models import OpenAIModel, OpenAIModelType
from devtools import debug


class Greet(Tool):
    def __init__(self, call_timeout: float = 1):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="text",
                                          desc='This is the text that will be displayed to the guests on the monitor')

    def do(self):
        print(self.text_arg.val)

    def get_desc(self) -> str:
        return "This tool is connected with a monitor in our house and allows you to send a message to our guests"


class TestOpenAIModel(Unittest):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def setup(cls):
        cls.model = OpenAIModel(model_type=OpenAIModelType.GPT_4)
        cls.greet_tool = Greet()

        cls.say_hi = Entry(Speaker(role=Role.USER), msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        cls.repetition = Entry(Speaker(role=Role.USER), msg='Can you please repeat what I said above in its entirety?')
        cls.greet_request = Entry(Speaker(role=Role.USER), msg='Please greet our guests with any message you see fit')
        cls.multi_tool_entry = Entry(Speaker(role=Role.USER), msg='Please perform multiple tool actions')

        cls.default_options = Options()
        cls.greet_tool_docs = Greet().get_json_doc(application_name=f'monitor')
        cls.tool_allowed_options = Options(tool_options=ToolOptions(call_allowed=True))

    # def test_chunk_text(self):
    #     context = GenerationContext(entries=[self.say_hi], docs=[])
    #     generation = self.model.get_generation(context, self.default_options)
    #     self.log_result(context, generation)

    # def test_test_stream(self):
    #     context = GenerationContext(entries=[self.say_hi], docs=[])
    #     generation = self.model.get_generation(context, self.default_options)
    #
    #     def exhaust():
    #         for chunk in generation:
    #             _ = chunk.get_text()
    #
    #     threading.Thread(target=exhaust).start()
    #     async def print_stream():
    #         async for text in generation.get_text_stream():
    #             print(text, end='')
    #
    #     asyncio.run(print_stream())

    def test_simple_tool_call(self):
        context = GenerationContext(entries=[self.greet_request], docs=[self.greet_tool_docs])
        generation = self.model.get_generation(context, self.tool_allowed_options)
        self.log_result(context, generation)
    #
    # def test_multi_tool_call(self):
    #     context = GenerationContext(entries=[self.multi_tool_entry], docs=[self.greet_tool_docs])
    #     generation = self.model.get_generation(context, self.tool_allowed_options)
    #     self._print_generation_chunks(generation)
    #
    # def test_text_and_function_call(self):
    #     context = GenerationContext(entries=[self.say_hi, self.greet_request], docs=[self.greet_tool_docs])
    #     generation = self.model.get_generation(context, self.tool_allowed_options)
    #     self._print_generation_chunks(generation)
    #
    # def test_remembers_conversation(self):
    #     context = GenerationContext(entries=[self.say_hi, self.repetition], docs=[])
    #     generation = self.model.get_generation(context, self.default_options)
    #     self._print_generation_chunks(generation)
    #
    # def test_remembers_tool_output(self):
    #     context = GenerationContext(entries=[self.greet_request, self.repetition], docs=[self.greet_tool_docs])
    #     generation = self.model.get_generation(context, self.tool_allowed_options)
    #     self._print_generation_chunks(generation)

    @staticmethod
    def log_result(context : GenerationContext, generation : Generation):
        prompts_context = [entry.get_content() for entry in context.entries]
        print(f'-> Prompts: \n {prompts_context}')
        print("->Generated Text Content:")


        call_map : dict[int, ToolCall] = {}
        printed_len = 0
        for chunk in generation:
            calls = chunk.get_calls()
            for partial_call in calls:
                the_index = partial_call.index
                if not partial_call.index in call_map:
                    call_map[the_index] = partial_call
                else:
                    call_map[the_index].update(partial_call=partial_call)

            chunk_text = chunk.get_text()

            if not chunk_text is None:
                printed_len += len(chunk_text)
                if printed_len > 150:
                    chunk_text = f'{chunk_text}\n'
                    printed_len = 0

                print(chunk_text, end='')
        print(f'-> Generated tool calls')
        for call in call_map.values():
            debug(call.get_args_dict())

        print()

if __name__ == '__main__':
    # model = OpenAIModel(model_type=OpenAIModelType.GPT_4)
    test = TestOpenAIModel()
    test.setup()
    test.execute_all()