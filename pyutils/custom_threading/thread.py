import threading
from threading import Thread

class CustomThread(Thread):
    def __new__(cls,target : callable, is_daemon = True):
        return threading.Thread(target=target,daemon=is_daemon)


class DaemonThread(CustomThread):
    def __new__(cls, target : callable):
        return CustomThread(target=target,is_daemon=True)