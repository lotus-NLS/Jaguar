import queue
import threading

class CustomQueue(queue.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_running = True
        self._get_duplicate_lock = threading.Lock()
        self._get_duplicate_cond = threading.Condition(self._get_duplicate_lock)

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)

        # Notify any threads waiting in get_duplicate
        with self._get_duplicate_cond:
            self._get_duplicate_cond.notify_all()

    def stop(self):
        self._is_running = False
        with self._get_duplicate_cond:
            self._get_duplicate_cond.notify_all()

    def get_duplicate(self):
        with self._get_duplicate_cond:
            while self._is_running and self.empty():
                self._get_duplicate_cond.wait()

            if not self._is_running:
                return None

            # Peek at the item from the queue
            item = self.queue[0]

            return item

