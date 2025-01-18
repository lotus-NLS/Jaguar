from api import Entry
from engine import LotusEngine
from engine.l0_engine.settings import LotusCredentials
from engine.l2_models import OpenAIModel, Context, Options
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from holytools.devtools import Unittest


# ---------------------------------------------------

class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.y_n_arg : ToolArg = ToolArg(name=f'YesOrNo', choices=[f'y', 'n'])

    def do(self):
        pass

    def get_desc(self) -> str:
        return f'Answers the user query about the target message with yes(y) or no(n)'

    def get_args(self) -> list[ToolArg]:
        return [self.y_n_arg]


class SemanticUnittest(Unittest):
    @classmethod
    def setUpClass(cls):
        configs = LotusCredentials()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.get_openai_apikey())

    def assertProperty(self, msg : str, prop : str):
        yn = YesNoTool()
        prop = (f'Please evaluate whether or not the following #property holds for the given #msg'
                          f'    - #property: {prop}'
                          f'    - #msg {msg}')
        entries = [Entry.user(msg=prop)]
        docs = [yn.get_doc()]
        context = Context(entries=entries, docs=docs)

        generation = self.model.get_generation(context=context, options=Options.text_only())
        generation.exhaust()
        text, calls = generation.get_text(), generation.get_tool_calls()
        print(f'-> Generated text: {text}')

        context += Context.singleton(entry=Entry.agent(msg=text))
        options = Options.require_call(tool_name=yn.get_name())
        yn_generation = self.model.get_generation(context=context, options=options)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(tool_call=calls[0])

        print(f'\"{prop}\": {yn.y_n_arg.get_value()}')
        self.assertTrue(yn.y_n_arg.get_value() == 'y')


class HardwareTask(SemanticUnittest):
    def test_components_there(self):
        engine = LotusEngine()
        #answer = engine.resarch_routine(workflowy=Workflowy._hardware_summary(),
        #                                query=f'Please give me a summary of my hardware', max_steps=5)

        property_query = (f'The ##Eval statement gives information about each of the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard')
        answer = 'GOTO: '
        self.assertProperty(msg=answer, prop=property_query)


if __name__ == "__main__":
    HardwareTask.execute_all()