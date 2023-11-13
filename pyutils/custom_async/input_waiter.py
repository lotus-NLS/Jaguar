from queue import Queue

class InputWaiter:
    def __init__(self):
        self.q = Queue()

    def clear(self):
        self.q = Queue()

    def write(self, value):
        self.q.put(value)

    def read(self):
        return self.q.get()
