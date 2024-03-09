from __future__ import annotations

import threading

from api import Entry, Role, Speaker
from engine.l5_singletons import Response, Handler, Task, TaskQueue
from engine.l3_models import LLM, Context, Options, Generation
from engine.l3_models import OpenAIModel
from engine.l2_os import OS, TextEditor
from engine.l1_agent.protocol import Identity

# ---------------------------------------------------------

class Agent(Handler):
    def __init__(self, model : LLM = OpenAIModel(), identity : Identity = Identity.GOTO()):
        super().__init__()
        # context
        self.identity : Identity = identity
        self.context: Context = Context()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # processing
        self.os : OS = OS(workspace_types=[TextEditor])
        self.model: LLM = model

    # ---------------------------------------------------
    # Main routine

    def handle(self, task: Task) -> Response:
        generation = self.get_next(options=Options.from_task(task=task))
        response = Response(text_stream=generation.get_text_stream())
        threading.Thread(target=self.process,args=(generation,)).start()
        return response


    def get_next(self, options: Options = Options()) -> Generation:
        context = Context(docs=self.os.get_docs(), entries=self.get_basic_entries())
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, do_feedback : bool = True):
        generation.exhaust()
        entry = Entry.as_agent(msg=generation.get_text())
        self.context.add_entry(entry=entry)
        call_map = generation.get_call_map()
        if not call_map.is_empty():
            self.os.handle_calls(call_map=call_map)
            if do_feedback:
                self.send_feedback(generation=generation)


    def send_feedback(self, generation : Generation):
        log_msg = '##Automatic message: The user has been provided with the function output with very brief summary/feedback'
        feedback_entry = Entry.as_system(msg=log_msg)
        new_generation = self.model.get_text_generation(entries=self.get_basic_entries() + [feedback_entry])
        for chunk in new_generation:
            text = chunk.get_text()
            generation.text_queue.put(text)

    # ---------------------------------------------------
    # Actions and context

    @classmethod
    def as_speaker(cls) -> Speaker:
        return Speaker(role=Role.AGENT, name=cls.__name__)

    def get_basic_entries(self) -> list[Entry]:
        basic_entries = [Entry(speaker=Speaker(role=Role.SYSTEM), msg=self.identity.get_str())]
        basic_entries += self.context

        return basic_entries

