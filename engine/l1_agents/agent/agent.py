from __future__ import annotations

from openai import APITimeoutError

from engine.l1_agents.guidance import Identity, StepInfo
from engine.l2_models import Generation
from engine.l2_models.context import Entry, Context
from engine.l2_models.generation.pipe import TextPipe
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolOutput
from holytools.logging import LogLevel, Loggable


# ---------------------------------------------------------

class Agent(Loggable):
    def __init__(self, model : LLM, aos : AOS, identity : Identity = Identity.GOTO()):
        super().__init__()
        self.model: LLM = model
        self.aos : AOS = aos
        self.identity : Identity = identity

        self.memory: list[Entry] = []

    # ---------------------------------------------------
    # Main routine

    # TODO: Re-introduce reports on task level
    #             if with_report:
    #                 entries = self.get_active_context().entries+[self.get_feedback_request()]
    #                 evaluation = self.model.get_text_generation(entries=entries)
    #                 self.process(generation=evaluation, pipe=pipe)

    # @classmethod
    # def get_feedback_request(cls) -> Entry:
    #     log_msg = '##Automatic message: Provide the user with an update'
    #     return Entry.user(msg=log_msg)

    def handle(self, task: StepInfo) -> TextPipe:
        if task.memory_update:
            self.memory.append(task.memory_update)
        context = self.get_context()
        if task.notice:
            context += Context.singleton(entry=task.notice)

        try:
            pipe = TextPipe()
            step = self.model.get_generation(context=context, options=task.get_options())
            self.write(generation=step, pipe=pipe)
            self.act(generation=step)
        except APITimeoutError:
            error_msg = f'OpenAI API request timed out after {self.model.inf_timeout} seconds'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            pipe = TextPipe.failed()

        return pipe

    def get_context(self) -> Context:
        context = Context(entries=[self.identity.as_system_entry()])
        context += Context.from_aos(aos=self.aos)
        context += Context(entries=self.memory)

        return context

    def write(self, generation : Generation, pipe : TextPipe):
        for chunk in generation:
            pipe.put(chunk.get_text())
        self.memory.append(Entry.agent(msg=generation.get_text()))
        pipe.stop()

    def act(self, generation : Generation):
        tool_calls = generation.get_tool_calls()
        tools_map = {tool.get_name(): tool for tool in self.aos.get_tools()}
        outputs : list[ToolOutput] = []
        for call in tool_calls:
            try:
                tool = tools_map[call.name]
                outputs += [tool.execute(tool_call=call)]
            except KeyError:
                self.log(f'No tool found with name {call.name}', level=LogLevel.ERROR)
                outputs += [ToolOutput.not_found(name=call.name)]
            except Exception as e:
                outputs += [ToolOutput.failed(name=call.name, reason=e)]

        for out in outputs:
            self.memory.append(Entry.from_tool_output(out))


    # ---------------------------------------------------
    # context

    def is_working(self) -> bool:
        return self.aos.workspace_engage()

    def get_system_prompt(self) -> Entry:
        system_msg = f'{self.identity.as_str()}\n'
        return Entry.system(msg=system_msg)