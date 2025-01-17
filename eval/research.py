from api import Entry
from engine import LotusEngine
from engine.l1_agents import Workflowy
from holytools.devtools import Unittest

from engine.l0_engine.settings import LotusCredentials
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from engine.l2_models import OpenAIModel, Context, Options


# ---------------------------------------------------

class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.y_n_arg : ToolArg = ToolArg(name=f'YesOrNo', choices=[f'y', 'n'])

    def do(self):
        pass

    def get_desc(self) -> str:
        return f'Answer a query with yes or no'

    def get_args(self) -> list[ToolArg]:
        return [self.y_n_arg]


class SemanticUnittest(Unittest):
    @classmethod
    def setUpClass(cls):
        configs = LotusCredentials()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.get_openai_apikey())

    def assertProperty(self, msg : str, property_query : str):
        yn = YesNoTool()
        entries = [Entry.agent(msg=msg), Entry.agent(msg=property_query)]
        docs = [yn.get_doc()]
        contet = Context(entries=entries, docs=docs)

        generation = self.model.get_generation(context=contet, options=Options.require_call(tool_name=f'YesNoTool'))
        generation.exhaust()
        text, calls = generation.get_text(), generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(tool_call=calls[0])

        print(f'\"{property_query}\": {yn.y_n_arg.get_value()}')
        self.assertTrue(yn.y_n_arg.get_value() == 'y')

class HardwareTask(SemanticUnittest):
    def test_components_there(self):
        engine = LotusEngine()
        answer = engine.query_routine(workflowy=Workflowy.hardware_summary(),
                                      query=f'Please give me a summary of my hardware', max_steps=5)

        property_query = (f'The given answer provdes information about the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard')
        self.assertProperty(msg=answer, property_query=property_query)


if __name__ == "__main__":
    HardwareTask.execute_all()