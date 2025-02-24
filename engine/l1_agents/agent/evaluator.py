from engine.l2_models import InfOptions
from engine.l2_models.language import Entry, Context
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import Tool, ToolArg


class Evaluator:
    def __init__(self, model: LLM):
        self.model : LLM = model

    def evaluateProperty(self, msg : str, prop : str) -> bool:
        yn = YesNoTool()
        query = (f'Please evaluate whether or not the following #property holds for the given #msg\n'
                          f'    - #property: \"{prop}\"\n'
                          f'    - #msg     : \"{msg}\"')
        entries = [Entry.user(msg=query)]
        docs = [yn.get_doc()]
        context = Context(entries=entries, docs=docs)

        generation = self.model.get_generation(context=context, options=InfOptions.text_only())
        generation.exhaust()
        eval_text, calls = generation.get_text(), generation.get_tool_calls()

        context += Context.singleton(entry=Entry.agent(msg=eval_text))
        options = InfOptions.require_call(tool_name=yn.get_name())
        yn_generation = self.model.get_generation(context=context, options=options)
        yn_generation.exhaust()
        text, calls = yn_generation.get_text(), yn_generation.get_tool_calls()

        yn.execute(tool_call=calls[0])
        return yn.y_n_arg.get_value() == 'y'


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