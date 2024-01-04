import threading, logging
import inspect
from collections.abc import Iterable

class CustomThread(threading.Thread):
    def __init__(self, target: callable, is_daemon=True, args: Iterable = ()):
        super().__init__(target=target, daemon=is_daemon, args=args)
        frame_record = inspect.stack()[2]
        self.target = target
        self.originating_method = frame_record[3]
        self.originating_module = inspect.getmodule(frame_record[0]).__name__

    def get_full_thread_info(self):
        return f"{self.originating_module}/{self.originating_method}/{self.target.__name__}"


    @classmethod
    def print_active_customthreads(cls):
        logging.info(f'Currently running custom threads:')
        for thread in threading.enumerate():
            if isinstance(thread,cls):
                logging.info(thread.get_full_thread_info())

class DaemonThread(CustomThread):
    def __init__(self, target: callable, args: Iterable = ()):
        super().__init__(target=target, is_daemon=True, args=args)