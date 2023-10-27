import queue
from pyutils import DaemonThread
from queue import Queue
from typing import Callable

from .entry import Entry


class Channel:
    def __init__(self):
        self.listener_loggers: list[Callable[[Entry], None]] = []
        self._message_queue : Queue[Entry] = queue.Queue()
        self._is_running = True

        monitor_thread = DaemonThread(target=self._process_queue)
        monitor_thread.start()

    # ------------------------------
    # Setup

    def _process_queue(self):
        while self._is_running:
            try:
                entry = self._message_queue.get(block=True, timeout=0.1)
                [logger(entry) for logger in self.listener_loggers]
            except queue.Empty:
                pass

    # ------------------------------
    # Other

    def broadcast_message(self, entry : Entry):
        self._message_queue.put(entry)
