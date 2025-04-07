from engine.l2_models import InfConfig
from engine.l2_models.language import Message, Context
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg

# ---------------------------------------------------------

class Evaluator:
    def __init__(self, model: LLM):
        self.model : LLM = model

    def evaluateProperty(self, report : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{report}\"')
        entries = [Message.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(messages=entries, docs=docs)

        generation = self.model.get_generation(context=context, config=InfConfig.text_only())
        generation.exhaust()
        eval_text, calls = generation.get_text(), generation.get_tool_calls()

        context += Context.singleton(entry=Message.agent(msg=eval_text))
        options = InfConfig(required_tool=yn)
        yn_generation = self.model.get_generation(context=context, config=options)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()
        yn.execute(args_dict=calls[0].get_args_dict())

        print(f'+------------------------+')
        print(f'Query: {query}')
        print(f'Agent: {eval_text}')
        print(f'Answer: {yn.y_n_arg.get_value() == "y"}')

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