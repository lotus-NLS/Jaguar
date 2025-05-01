from engine.l0_main.lotus_engine import LotusEngine
from engine.l0_main.settings import LotusCredentials
from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Message, Context
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg
from eval.cenarios.taskprovider import TaskProvider
from holytools.devtools import Unittest


# ---------------------------------------------------

class NLU(Unittest):
    @classmethod
    def setUpClass(cls):
        configs : LotusCredentials = LotusCredentials.from_file()
        cls.model : LLM = OpenAIModel.default_model(api_key=configs.openai_api_key)
        cls.task_provider : TaskProvider = TaskProvider()
        cls.engine : LotusEngine = LotusEngine()

    def evaluateProperty(self, msg : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{msg}\"')
        entries = [Message.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(messages=entries, docs=docs)

        generation = self.model.get_generation(context=context, config=InfConfig.text_only())
        generation.exhaust()
        eval_text, calls = generation.get_text(), generation.get_tool_calls()

        context += Context.singleton(entry=Message.agent(msg=eval_text))
        yn_inf_config = InfConfig(required_tool=yn)
        yn_generation = self.model.get_generation(context=context, config=yn_inf_config)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        self.assertTrue(len(calls) == 1)
        yn.execute(args_dict=calls[0].get_args_dict())

        print(f'\n- Evaluation results:')
        print(f'Query: {query}\n'
              f'Eval : {eval_text}\n'
              f'Answer: {yn.y_n_arg.get_value()}')
        return yn.y_n_arg.get_value() == 'y'

class YesNoTool(Tool):
    def __init__(self):
        super().__init__()
        self.y_n_arg : ToolArg = ToolArg(name=f'YesOrNo', choices=[f'y', 'n'])

    def _do(self):
        pass

    def get_desc(self) -> str:
        return f'Answers the user query about the target message with yes(y) or no(n)'

    def get_args(self) -> list[ToolArg]:
        return [self.y_n_arg]

