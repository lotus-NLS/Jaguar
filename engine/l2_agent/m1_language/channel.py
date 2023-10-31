import queue
from queue import Queue
from typing import Callable
from threading import Lock


from .entry import Entry

# ----------------------------------------------------


from threading import Lock

class SpeakerStaff:
    def __init__(self):
        self.lock = Lock()
        self.holder = None

    def acquire(self, holder):
        acquired = self.lock.acquire(blocking=False)  # Try to acquire the lock
        if acquired:
            self.holder = holder
        return acquired

    def release(self):
        self.lock.release()
        self.holder = None

    def current_holder(self):
        return self.holder
    

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
        self.speaker_staff : SpeakerStaff = SpeakerStaff()

    def acquire_staff(self, holder):
        self.speaker_staff.acquire(holder=holder)

    def release_staff(self):
        self.speaker_staff.release()

    # ------------------------------
    # Other

    def get_stream(self) -> Stream:
        new_stream = Stream()
        self.stream_list.append(new_stream)
        return new_stream

    def broadcast(self, entry : Entry):
        active_streams = [stream for stream in self.stream_list if stream.is_active]
        for stream in active_streams:
            stream.put(entry)