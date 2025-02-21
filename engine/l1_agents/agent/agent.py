from __future__ import annotations

from openai import APITimeoutError

from engine.l1_agents.guidance import Identity
from engine.l1_agents.guidance.workflowy import Workflowy, Mandate
from engine.l2_models import Generation, InfOptions
from engine.l2_models.context import Entry, Context
from engine.l2_models.generation.pipe import TextPipe
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.workspace import Workspace
from holytools.logging import LogLevel, Loggable


# ---------------------------------------------------------

class Agent(Loggable):
    def __init__(self, model : LLM, aos : AOS, identity : Identity = Identity.GOTO()):
        super().__init__()
        self.model: LLM = model
        self.aos : AOS = aos
        self.workflowy : Workflowy = Workflowy()
        self.identity : Identity = identity

        self.memory: list[Entry] = []

    def converse(self, msg : str) -> TextPipe:
        self.memory.append(Entry.user(msg=msg))
        return self.handle()

    def work(self, mandate : Mandate, max_steps : int):
        self.workflowy.root = mandate
        self.workflowy.is_active = True
        for j in range(max_steps):
            self.handle()
            if not self.is_working():
                print(f'Finished work mode after {j+1} steps')
                break
        self.workflowy.root = None

    # ---------------------------------------------------
    # Main routine

    def handle(self, inf_options : InfOptions = InfOptions()) -> TextPipe:
        context = self.get_context()

        try:
            pipe = TextPipe()
            generation = self.model.get_generation(context=context, options=inf_options)
            self.write(generation=generation, pipe=pipe)
            self.act(generation=generation)
        except APITimeoutError:
            error_msg = f'OpenAI API request timed out after {inf_options.timeout} seconds'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            pipe = TextPipe.failed()

        return pipe

    def write(self, generation : Generation, pipe : TextPipe):
        for chunk in generation:
            pipe.put(chunk.get_text())
        response_entry = Entry.agent(msg=generation.get_text())
        self.update_memory(entry=response_entry)
        pipe.stop()

    def act(self, generation : Generation):
        tool_calls = generation.get_tool_calls()
        tools_map = {tool.get_name(): tool for tool in self.aos.get_tools() + self.workflowy.get_actions()}
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

    def update_memory(self, entry : Entry):
        self.memory.append(entry)

    def is_working(self):
        return not self.workflowy.root is None

    def get_context(self) -> Context:
        context = Context(entries=[self.identity.as_system_entry()])
        context += Context.from_aos(aos=self.aos)
        context += Context(entries=self.memory)

        if self.is_working():
            workflowy_content = Entry.tool(self.workflowy.get_text(), name=self.workflowy.get_name())
            context += Context(entries=[workflowy_content], docs=self.workflowy.get_action_docs())
            work_entry = Entry.system(msg='You are currently in work mode and cannot converse with the user. '
                                          'Your current tasks are outlined in the Workflowy workspace')
            context += Context.singleton(entry=work_entry)

        return context