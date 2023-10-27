from lotusEngine.pyutils import DaemonThread
from typing import Optional
from lotusEngine.pyutils import InputWaiter
import sys

# ---------------------------------------------------------

class UserIO:
    def __init__(self, text_logger : callable = None):
        self.input_waiter_list : list[InputWaiter] = []

        no_newline_print = lambda the_str: (print(the_str, end=''), sys.stdout.flush())
        self.str_logger : callable = text_logger if not text_logger is None else no_newline_print

    def launch(self):
        thread = DaemonThread(self.loop)
        thread.start()


    def loop(self):
        while True:
            user_input = input('')
            if len(self.input_waiter_list) > 0:
                self.input_waiter_list[-1].write(user_input)
                del self.input_waiter_list[-1]

    def get_user_msg(self, prompt_msg : Optional[str] = None):
        if not prompt_msg is None:
            print(prompt_msg)

        input_retriever = InputWaiter()
        self.input_waiter_list.append(input_retriever)
        return input_retriever.read()


    def get_confirmation(self, msg : Optional[str] = None) -> bool:
        while True:
            lowercase_user_input = self.get_user_msg(prompt_msg=msg).lower()
            if lowercase_user_input in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")

        return lowercase_user_input == 'y'


    def print_str(self, the_str : str):
        self.str_logger(the_str)

user_io = UserIO()