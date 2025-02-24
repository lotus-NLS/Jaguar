from __future__ import annotations

from typing import Iterator

from openai import APITimeoutError, APIError

from engine.l1_agents.guidance import Identity
from engine.l1_agents.guidance.tasktracker import TaskTracker, Task
from engine.l2_models import Generation, InfOptions
from engine.l2_models.language import Entry, Context
from engine.l2_models.generation.step import TextPipe, Step
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
        self.task_tracker : TaskTracker = TaskTracker()
        self.aos : AOS = aos
        self.identity : Identity = identity
        self.memory: list[Entry] = []

        self.aos.add_workspace(ws=self.task_tracker)
        for ws in self.aos.get_workspaces(active_only=False):
            hook = self.get_freeze_hook(ws=ws)
            ws.close_action.add_prehook(hook)

    def converse(self, msg : str) -> Step:
        self.memory.append(Entry.user(msg=msg))
        return self.handle()

    def work(self, task : Task, max_steps : int) -> Iterator[Step]:
        self.task_tracker.open_action.do()
        self.task_tracker.root = task
        require_update = InfOptions.require_call(tool_name=self.aos.update_tool.get_name())
        report_frequency = 4

        self.update_memory(entry=Entry.system(msg=f'Now entering work mode'))
        for j in range(max_steps):
            inf_options = require_update if (j+1) % report_frequency == 0 else InfOptions()
            yield self.handle(inf_options=inf_options)
            if not self.is_working():
                break

        if self.is_working():
            self.task_tracker.close_action.do()

        self.update_memory(entry=Entry.system(msg=f'Now leaving work mode. Please review the objective and provide an execute summary of your results '
                                                  f'with regard to this objective. Keep it to 60 words or less, so about 3-4 sentences.'
                                                  f'This report will be used to evaluate the success or failure of the objective.'))
        yield self.handle(inf_options=InfOptions.text_only(max_output_tokens=100))

    # ---------------------------------------------------
    # Main routine

    def handle(self, inf_options : InfOptions = InfOptions()) -> Step:
        context = self.get_context()

        try:
            generation = self.model.get_generation(context=context, options=inf_options)
            pipe = self.write(generation=generation)
            self.act(generation=generation)
        except APITimeoutError:
            error_msg = f'OpenAI API request timed out after {inf_options.timeout} seconds'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            return Step.failed(context=context)
        except APIError:
            error_msg = f'OpenAI API request failed'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            return Step.failed(context=context)

        return Step(text_pipe=pipe, ckpt_label=self.aos.get_steplabel(), generation_ctx=context)

    def write(self, generation : Generation):
        pipe = TextPipe()
        for chunk in generation:
            pipe.put(chunk.get_text())
        pipe.stop()

        text = generation.get_text()
        if text:
            self.update_memory(entry=Entry.agent(msg=text))

        return pipe

    def act(self, generation : Generation) -> list[ToolOutput]:
        tool_calls = generation.get_tool_calls()
        tools_map = {t.get_name(): t for t in self.aos.get_tools(with_update=self.is_working())}
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

        return outputs

    # ---------------------------------------------------
    # language

    def get_freeze_hook(self, ws : Workspace):
        def freeze_ws(frozen_ws: Workspace = ws):
            entry = Entry.from_workspace(ws=frozen_ws)
            entry.add(msg=f'Closed workspace {frozen_ws.get_name()} with following final state:', at_start=True)
            self.update_memory(entry=entry)
            return frozen_ws
        return freeze_ws

    def update_memory(self, entry : Entry):
        self.memory.append(entry)

    def get_context(self) -> Context:
        context = Context(entries=[self.identity.as_system_entry()])
        context += Context.from_aos(aos=self.aos, with_update=self.is_working())
        context += Context(entries=self.memory)

        msg = (f'You are currently in work mode and cannot converse with the user. '
              f'Your current tasks are outlined in the {TaskTracker.__name__} workspace. '
              'Upon completing these tasks or closing the workspace you will automatically return to conversation mode')
        if self.is_working():
            work_entry = Entry.system(msg=msg)
            context += Context.singleton(entry=work_entry)

        return context

    def is_working(self) -> bool:
        return self.task_tracker.is_active