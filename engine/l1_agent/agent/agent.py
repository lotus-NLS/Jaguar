from __future__ import annotations

import threading
from hollarek.logging import LogLevel
from api import Entry, Role, Speaker
from engine.l5_singletons import Response, Handler, Task, TaskQueue, TextPipeline
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
            pipeline = TextPipeline()
            def process_generation():
                self.process(generation=generation, pipeline=pipeline)
            threading.Thread(target=process_generation).start()
            response = Response(text_queue=pipeline)
        except Exception as e:
            self.log(f'Error in getting generation: {e}', level=LogLevel.ERROR)
            response = Response.failed()
        return response


    def get_next(self, options: Options = Options()) -> Generation:
        context = self.get_active_context()
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, pipeline : TextPipeline, with_report : bool = True):
        for chunk in generation:
            pipeline.put(chunk.get_text())
        response_entry = Entry.as_agent(msg=generation.get_text())
        self.memory.add_entry(entry=response_entry)
        self.os.handle_calls(call_map=generation.get_call_map())
        if with_report:
            self.send_feedback(pipeline=pipeline)
        pipeline.stop()


    def send_feedback(self, pipeline : TextPipeline):
        log_msg = '##Automatic message: The user has been provided with the function output with very brief summary/feedback'
        feedback_entry = Entry.as_system(msg=log_msg)
        new_generation = self.model.get_text_generation(entries=self.get_active_context().entries + [feedback_entry])
        for chunk in new_generation:
            text = chunk.get_text()
            pipeline.put(text)

    # ---------------------------------------------------
    # Actions and context

    @classmethod
    def as_speaker(cls) -> Speaker:
        return Speaker(role=Role.AGENT, name=cls.__name__)


    def get_active_context(self) -> Context:
        context = Context()
        system_prompt = Entry.as_system(msg=self.identity.get_str())
        context.add_entry(system_prompt)

        context += self.os.get_context()
        context += self.memory

        return context