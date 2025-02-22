from __future__ import annotations

from openai import APITimeoutError

from engine.l1_agents.guidance import Identity
from engine.l1_agents.guidance.tasktracker import TaskTracker, Task
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
        self.task_tracker : TaskTracker = TaskTracker()
        self.identity : Identity = identity

        self.memory: list[Entry] = []
        self.aos.add_workspace(ws=self.task_tracker)

    def converse(self, msg : str) -> TextPipe:
        self.memory.append(Entry.user(msg=msg))
        return self.handle()

    def work(self, task : Task, max_steps : int):
        self.task_tracker.open_action.do()
        self.task_tracker.root = task
        for j in range(max_steps):
            self.handle()
            if not self.is_working():
                print(f'Finished work mode after {j+1} steps')
                break

        if self.is_working():
            self.freeze_final_state(ws=self.task_tracker)
            self.task_tracker.close_action.do()

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
        pipe.stop()

        text = generation.get_text()
        if text:
            self.update_memory(entry=Entry.agent(msg=text))

    def act(self, generation : Generation):
        tool_calls = generation.get_tool_calls()
        tools_map = {t.get_name(): t for t in self.aos.get_tools(with_update=self.is_working())}
        outputs : list[ToolOutput] = []

        for call in tool_calls:
            if 'close' in call.name:
                ws_name, _ = call.name.split('_')
                ws = self.aos.get_ws(name=ws_name)
                self.freeze_final_state(ws)
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

    def freeze_final_state(self, ws : Workspace):
        e1 = Entry.tool(f'Closed workspace {ws.get_name()} with following final state:', name=ws.get_name())
        e2 = Entry.from_workspace(ws=ws)
        self.update_memory(entry=e1)
        self.update_memory(entry=e2)

    # ---------------------------------------------------
    # context


    def is_working(self) -> bool:
        return self.task_tracker.is_active

    def update_memory(self, entry : Entry):
        self.memory.append(entry)

    def get_context(self) -> Context:
        context = Context(entries=[self.identity.as_system_entry()])
        context += Context.from_aos(aos=self.aos)
        context += Context(entries=self.memory)

        if self.is_working():
            work_entry = Entry.system(msg=f'You are currently in work mode and cannot converse with the user. '
                                          f'Your current tasks are outlined in the {TaskTracker.__name__} workspace.'
                                          'Upon completing these tasks or closing the workspace you will automatically return to conversation mode')
            context += Context.singleton(entry=work_entry)

        return context
