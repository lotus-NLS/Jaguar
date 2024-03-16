from __future__ import annotations

import queue
from queue import Queue
from typing import Optional, Iterator
from dataclasses import dataclass

from engine.l5_singletons.io.tasks import Task
from hollarek.logging import Loggable, LogLevel
from hollarek.templates import Dillable
from ..language.entry import Entry

# ----------------------------------------------
# Classes

@dataclass
class APIMessage(Dillable):
    def __init__(self, entry : Optional[Entry] = None, choice : Optional[bool] = None):
        self.user_id : str = 'default_id'
        self.task : Task
        self.bool_content : Optional[bool] = choice


class Pipe(Queue):
    def put(self, msg : Optional[str], *args, **kwargs):
        if msg is None:
            return
        if not isinstance(msg, str):
            raise TypeError("Can only put strings inTextQueue.")
        super().put(msg, *args, **kwargs)

    def get(self, *args, **kwargs) -> str:
        item = super().get(*args, **kwargs)
        return item

    def stop(self):
        self.put(Response.stop_token)


class Response(Loggable):
    stop_token = '⊥'

    def __init__(self, text_queue : Pipe):
        super().__init__()
        self.text_queue : Pipe = text_queue

    def get_text_stream(self) -> Iterator[str]:
        timeout = 10
        while True:
            try:
                text = self.text_queue.get(timeout=timeout)
            except queue.Empty:
                self.log(f'Text queue timed out after {timeout}s', level=LogLevel.WARNING)
                break
            except Exception as e:
                self.log(f'Error in getting text from queue: {e}', level=LogLevel.ERROR)
                break
            if text == self.stop_token:
                self.log(f'\nReceived stop token from text queue', level=LogLevel.DEBUG)
                break
            if not text:
                continue
            yield text


    @classmethod
    def failed(cls, msg : Optional[str] = None):
        pipeline : Pipe = Pipe()
        pipeline.put(msg)
        pipeline.stop()
        return cls(text_queue=pipeline)



