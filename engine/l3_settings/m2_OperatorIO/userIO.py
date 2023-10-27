from typing import Optional
from pyutils import InputWaiter
import sys

# ---------------------------------------------------------

# TODO: This should be an abstract class and server should implement userIO
class UserIO:
    def __init__(self, user_logger : callable = None):
        self.input_waiter_list : list[InputWaiter] = []

        no_newline_print = lambda the_str: (print(the_str, end=''), sys.stdout.flush())
        self.str_logger : callable = user_logger if not user_logger is None else no_newline_print
        self.input_retriever : Optional[callable] = None


    def get_user_msg(self) -> str:
        pass

    def get_confirmation(self, msg : Optional[str] = None) -> bool:
        _ = msg
        while True:
            lowercase_user_input = self.get_user_msg().lower()
            if lowercase_user_input in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")

        return lowercase_user_input == 'y'


    def print_str(self, the_str : str):
        self.str_logger(the_str)

user_io = UserIO()