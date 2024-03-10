from __future__ import annotations

import threading
from hollarek.logging import LogLevel
from api import Entry
from engine.l5_singletons import Response, Handler, Task, TaskQueue, Pipe
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
        self.memory: Context = Context()
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # processing
        self.os : OS = OS(workspace_types=[TextEditor])
        self.model: LLM = model

    # ---------------------------------------------------
    # Main routine

    def handle(self, task: Task) -> Response:
        for entry in task.new_entries:
            self.memory.add_entry(entry=entry)
        try:
            generation = self.get_next(options=Options.from_task(task=task))
            pipe = Pipe()
            def do():
                self.process(generation=generation, pipe=pipe)
            threading.Thread(target=do).start()
            response = Response(text_queue=pipe)
        except Exception as e:
            self.log(f'Error in getting generation: {e}', level=LogLevel.ERROR)
            response = Response.failed()
        return response


    def get_next(self, options: Options = Options()) -> Generation:
        context = self.get_active_context()
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, pipe : Pipe, with_report : bool = True):
        for chunk in generation:
            pipe.put(chunk.get_text())
        response_entry = Entry.as_agent(msg=generation.get_text())
        self.memory.add_entry(entry=response_entry)

        call_map = generation.get_call_map()
        if not call_map.is_empty():
            self.os.handle_calls(call_map=call_map)
            if with_report:
                self.memory.add_entry(entry=self.get_feedback_request())
                feedback = self.get_next(options=Options.text_only())
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
        context += self.memory

        return context


    def get_system_prompt(self) -> Entry:
        return Entry.as_system(msg=self.identity.get_str())