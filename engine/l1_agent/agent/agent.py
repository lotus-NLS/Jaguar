from __future__ import annotations

import asyncio
from api import Entry, Role, Speaker
from engine.l5_singletons import ServerResponse, Entity, Task, TaskQueue
from engine.l4_tools import CallMap
from engine.l3_models import LLM, GenerationContext, Options, Generation, Chunk
from engine.l3_models import OpenAIModel
from engine.l2_os import OS, Host, TextEditor
from engine.l1_agent.protocol import Identity, Core

# ---------------------------------------------------------

class Agent(Entity):
    def __init__(self, model : LLM = OpenAIModel(), identity : Identity = Identity(core=Core.GOTO)):
        super().__init__()
        # context
        self.identity : Identity = identity
        self.log: list[Entry] = []
        self.task_queue : TaskQueue[Task] = TaskQueue()

        # processing
        self.os : OS = OS(workspace_types=[Host, TextEditor])
        self.call_map : CallMap = CallMap()
        self.model: LLM = model

    # ---------------------------------------------------
    # Main routine

    async def handle(self, task: Task) -> ServerResponse:
        generation = await self.get_next(options=Options.from_task(task=task))
        response = ServerResponse(text_stream=await generation.get_text_stream())
        await asyncio.create_task(self.process(generation=generation))
        return response


    async def get_next(self, options: Options = Options()) -> Generation:
        context = GenerationContext(docs=self.os.get_docs(), entries=self.get_basic_entries())
        return self.model.get_generation(context=context, options=options)


    def process(self, generation : Generation, do_feedback : bool = True):
        for chunk in generation:
            self.store_info(chunk=chunk)
        if not self.call_map.is_empty():
            self.os.handle_calls(call_map=self.call_map)
            if do_feedback:
                self.send_feedback(generation=generation)
        generation.stop()


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
        basic_entries += self.log

        return basic_entries

    def store_info(self, chunk : Chunk):
        self.call_map.add(chunk.get_call_map())