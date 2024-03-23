from __future__ import annotations

import threading
from hollarek.core.logging import LogLevel, Loggable
from func_timeout import FunctionTimedOut
from api import Entry, TextPipe
from engine.l3_models import LLM, Context, Options, Generation
from engine.l3_models import OpenAIModel
from engine.l2_os import OS, LotusTerminal
from engine.l1_agent.protocol import Identity, Task


# ---------------------------------------------------------

class Agent(Loggable):
    def __init__(self, model : LLM = OpenAIModel.get_gpt4_turbo(), identity : Identity = Identity.GOTO()):
        super().__init__()
        # context
        self.identity : Identity = identity
        self.memory: list[Entry] = []
        # self.task_queue : TaskQueue[Task] = TaskQueue()

        # processing
        self.os : OS = OS(workspace_types=[LotusTerminal])
        self.model: LLM = model

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
            self.log(f'Error in getting generation: {e}', level=LogLevel.ERROR)
            pipe = TextPipe.failed()
        return pipe


    def get_next(self, options: Options = Options()) -> Generation:
        context = self.get_active_context()
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, pipe : TextPipe, with_report : bool = True):
        for chunk in generation:
            pipe.put(chunk.get_text())
        response_entry = Entry.as_agent(msg=generation.get_text())
        self.memory.append(response_entry)

        call_map = generation.get_call_map()
        if not call_map.is_empty():
            outputs = self.os.handle_calls(call_map=call_map)
            for out in outputs:
                self.memory.append(out.as_entry())
            if with_report:
                entries = self.get_active_context().entries + [self.get_feedback_request()]
                feedback = self.model.get_text_generation(entries=entries)
                self.process(generation=feedback, pipe=pipe)
        pipe.stop()


    @classmethod
    def get_feedback_request(cls) -> Entry:
        log_msg = '##Automatic message: The user has been provided with the function output with very brief summary/feedback'
        return Entry.as_system(msg=log_msg)


    # ---------------------------------------------------
    # context

    def get_active_context(self) -> Context:
        context = Context()
        context.add_entry(self.get_system_prompt())
        context += self.os.get_context()
        context += Context(entries=self.memory)

        return context

    def get_system_prompt(self) -> Entry:
        return Entry.as_system(msg=self.identity.get_str())