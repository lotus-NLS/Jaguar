import queue
import threading
from queue import Queue
from typing import Callable

from s4_conversation.ConversationEntry import ConversationEntry


class Channel:
    def __init__(self):
        self.participant_loggers: list[Callable[[ConversationEntry], None]] = []
        self._message_queue : Queue[ConversationEntry] = queue.Queue()
        self._is_running = True

        threading.Thread(target=self._process_queue).start()

    # ------------------------------
    # Setup

    def _process_queue(self):
        while self._is_running:
            try:
                entry = self._message_queue.get(block=True, timeout=0.1)
                [logger(entry) for logger in self.participant_loggers]
            except queue.Empty:
                pass

    # ------------------------------
    # Other

    def broadcast_message(self, entry : ConversationEntry):
        self._message_queue.put(entry)

    def stop_after_next_timeout(self):
        self._is_running = False