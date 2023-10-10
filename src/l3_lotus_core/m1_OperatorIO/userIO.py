import threading
from typing import Optional
from queue import Queue

class InputWaiter:
    def __init__(self):
        self.q = Queue()

    def write(self, value):
        self.q.put(value)

    def read(self):
        return self.q.get()


class UserIO:
    def __init__(self):
        self.input_waiter_list : list[InputWaiter] = []

    def launch(self):
        thread = threading.Thread(target=self.loop)
        thread.start()

    def loop(self):
        while True:
            user_input = input('')
            self.input_waiter_list[-1].write(user_input)
            del self.input_waiter_list[-1]

    def get_user_msg(self, prompt_msg : str = ''):
        if not prompt_msg == '':
            print(prompt_msg)

        input_retriever = InputWaiter()
        self.input_waiter_list.append(input_retriever)
        return input_retriever.read()


    def get_confirmation(self, msg : Optional[str] = None) -> bool:
        while True:
            user_input = self.get_user_msg(f'{msg}')
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")

        if user_input == 'y':
            return True
        else:
            return False

user_io = UserIO()
user_io.launch()