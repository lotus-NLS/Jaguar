import threading
from queue import Queue

class ReadBlocker:
    def __init__(self):
        self.q = Queue()

    def write(self, value):
        self.q.put(value)

    def read(self):
        return self.q.get()

class UserIO:
    def __init__(self):
        self.blockingObjects : list[ReadBlocker] = []

    def launch(self):
        thread = threading.Thread(target=self.loop)
        thread.start()

    def loop(self):
        while True:
            user_input = input('')
            self.blockingObjects[-1].write(user_input)
            del self.blockingObjects[-1]

    def get_user_msg(self, prompt_msg : str = ''):
        if not prompt_msg == '':
            print(prompt_msg)

        input_retriever = ReadBlocker()
        self.blockingObjects.append(input_retriever)
        return input_retriever.read()


    def get_confirmation(self) -> bool:
        while True:
            user_input = self.get_user_msg(f'')
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")


        if user_input == 'y':
            return True
        else:
            return False
#
# TODO: This object could be accessed from multiple threads so it should be made thread secure
# For example currently if get_user_msg is called from a side thread while it it is called and hasnt return in the main thread
# The main thread will still hold the IO stream and the second call will have to wait until that is done to get it
user_io = UserIO()
user_io.launch()