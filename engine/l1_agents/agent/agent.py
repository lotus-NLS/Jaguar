from __future__ import annotations

from queue import Queue

from openai import APITimeoutError

from engine.l1_agents.guidance import Identity, Step
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
        self.step_queue : Queue[Step] = Queue()

        self.memory: list[Entry] = []

    # ---------------------------------------------------
    # Main routine

    def handle(self, step: Step) -> TextPipe:
        context = self.get_context(work_mode=step.mode == 'work')
        inf_options = step.get_options()

        try:
            pipe = TextPipe()
            step = self.model.get_generation(context=context, options=inf_options)
            self.write(generation=step, pipe=pipe)
            self.act(generation=step)
        except APITimeoutError:
            error_msg = f'OpenAI API request timed out after {inf_options.timeout} seconds'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            pipe = TextPipe.failed()

        return pipe

    def update_memory(self, entry : Entry):
        self.memory.append(entry)

    def get_context(self, work_mode : bool = False) -> Context:
        context = Context(entries=[self.identity.as_system_entry()])
        context += Context(entries=self.memory)
        context += Context.from_aos(aos=self.aos)

        if work_mode:
            work_entry = Entry.system(msg='You are currently in work mode and cannot converse with the user')
            context += Context.singleton(entry=work_entry)

        return context

    def write(self, generation : Generation, pipe : TextPipe):
        for chunk in generation:
            pipe.put(chunk.get_text())
        response_entry = Entry.agent(msg=generation.get_text())
        self.update_memory(entry=response_entry)
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
            output_entry = Entry.from_tool_output(out)
            self.update_memory(output_entry)

    # ---------------------------------------------------
    # context

    def get_system_prompt(self) -> Entry:
        system_msg = f'{self.identity.as_str()}\n'
        return Entry.system(msg=system_msg)