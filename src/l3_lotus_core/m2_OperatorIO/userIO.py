import threading
from typing import Optional
from pyutils import InputWaiter


class UserIO:
    def __init__(self):
        self.input_waiter_list : list[InputWaiter] = []

    def launch(self):
        thread = threading.Thread(target=self.loop)
        thread.daemon = True
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

user_io = UserIO()