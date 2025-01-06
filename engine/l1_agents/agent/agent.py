from __future__ import annotations

import threading

from func_timeout import FunctionTimedOut

from api import Entry, TextPipe
from engine.l1_agents.protocol import Identity, Task
from engine.l2_models import Context, Generation
from engine.l2_models.models.llm import LLM
from engine.l3_aos import AOS
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

    def handle(self, task: Task) -> TextPipe:
        self.memory += task.new_entries
        try:
            step = self.model.get_generation(context=self.get_context(), options=task.get_options())
            pipe = TextPipe()
            def do():
                self.write(generation=step, pipe=pipe)
                self.act(generation=step)
            threading.Thread(target=do).start()
        except FunctionTimedOut as e:
            self.log(f'Attempt to retrieve generation timed out: {e}', level=LogLevel.WARNING)
            pipe = TextPipe.failed()
        except BaseException as e:
            self.log(f'Error in getting generation: {e.__repr__()}', level=LogLevel.ERROR)
            pipe = TextPipe.failed()
            raise e
        return pipe

    def write(self, generation : Generation, pipe : TextPipe):
        for chunk in generation:
            pipe.put(chunk.get_text())
        self.memory.append(Entry.agent(msg=generation.get_text()))
        pipe.stop()

    def act(self, generation : Generation):
        actions = generation.get_actions()
        outputs = self.aos.handle_actions(actions=actions)
        for out in outputs:
            self.memory.append(out.as_entry())


    # ---------------------------------------------------
    # context

    def get_context(self) -> Context:
        context = Context(entries=[self._get_system_prompt()])
        context += Context.from_aos(aos=self.aos)
        context += Context(entries=self.memory)

        return context

    def _get_system_prompt(self) -> Entry:
        system_msg = f'{self.identity.get_str()}\n'
        system_msg += f'Available workspaces: \n'
        for workspace in self.aos.get_workspaces():
            system_msg += f'- {workspace.get_name()}: {workspace.get_desc()}\n'
        system_msg += (f'The workspace has to be opened first in order for you to make use of it. '
                       f'The outlined functionalities will only then become available')
        return Entry.system(msg=system_msg)