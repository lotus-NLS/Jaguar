import queue
from pyutils import DaemonThread
from queue import Queue
from typing import Callable


from .entry import Entry

# ----------------------------------------------------

class Stream(Queue):
    def __init__(self):
        super().__init__()
        self.is_active : bool = True

    def close(self):
        self.put(None)
        self.is_active = False


class Channel:
    def __init__(self):
        self.listener_loggers: list[Callable[[Entry], None]] = []
        self._message_queue : Queue[Entry] = queue.Queue()
        self.stream_list : list[Stream] = []

    # ------------------------------
    # Other

    def get_stream(self) -> Stream:
        new_stream = Stream()
        self.stream_list.append(new_stream)
        return new_stream

    def broadcast_message(self, entry : Entry):
        active_streams = [stream for stream in self.stream_list if stream.is_active]
        for stream in active_streams:
            stream.put(entry)