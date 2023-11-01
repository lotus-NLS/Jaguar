from queue import Queue
from typing import Callable

from .language_types import Entry, SpeakerStaff, Stream


# ----------------------------------------------------


class Channel:
    def __init__(self):
        self.listener_loggers: list[Callable[[Entry], None]] = []
        self._message_queue : Queue[Entry] = Queue()
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