from __future__ import annotations

import threading

from func_timeout import FunctionTimedOut

from api import Entry, TextPipe
from engine.l1_agents.protocol import Identity, Task
from engine.l2_models import Context, Options, Generation
from engine.l2_models.models.llm import LLM
from engine.l3_aos import AOS, Terminal, FileExplorer, Browser, TextEditor
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

    def handle(self, task: Task) -> TextPipe:
        self.memory += task.new_entries
        try:
            generation = self.get_next(options=task.get_options())
            pipe = TextPipe()
            def do():
                self.process(generation=generation, pipe=pipe)
            threading.Thread(target=do).start()
        except FunctionTimedOut as e:
            self.log(f'Attempt to retrieve generation timed out: {e}', level=LogLevel.WARNING)
            pipe = TextPipe.failed()
        except BaseException as e:
            self.log(f'Error in getting generation: {e.__repr__()}', level=LogLevel.ERROR)
            pipe = TextPipe.failed()
            raise e
        return pipe


    def get_next(self, options: Options = Options()) -> Generation:
        context = self.get_active_context()
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, pipe : TextPipe, with_report : bool = True):
        for chunk in generation:
            pipe.put(chunk.get_text())
        response_entry = Entry.agent(msg=generation.get_text())
        self.memory.append(response_entry)

        call_map = generation.get_call_map()
        if not call_map.is_empty():
            outputs = self.aos.handle_calls(call_map=call_map)
            for out in outputs:
                self.memory.append(out.as_entry())
            if with_report:
                entries = self.get_active_context().entries+[self.get_feedback_request()]
                feedback = self.model.get_text_generation(entries=entries)
                self.process(generation=feedback, pipe=pipe)
        pipe.stop()

    @classmethod
    def get_feedback_request(cls) -> Entry:
        log_msg = '##Automatic message: Provide the user with an update'
        return Entry.user(msg=log_msg)

    # ---------------------------------------------------
    # context

    def get_active_context(self) -> Context:
        context = Context()
        context.add_entry(self.get_system_prompt())
        context += Context.from_aos(aos=self.aos)
        context += Context(entries=self.memory)

        return context

    def get_system_prompt(self) -> Entry:
        system_msg = f'{self.identity.get_str()}\n'
        system_msg += f'Available workspaces: \n'
        for workspace in self.aos.get_workspaces():
            system_msg += f'- {workspace.get_name()}: {workspace.get_desc()}\n'
        system_msg += (f'The workspace has to be opened first in order for you to make use of it. '
                       f'The outlined functionalities will only then become available')
        return Entry.system(msg=system_msg)