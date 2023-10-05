# import threading
# import time
# from queue import Queue
#
# class BlockingObject:
#     def __init__(self):
#         self.q = Queue()
#
#     def write(self, value):
#         self.q.put(value)
#
#     def read(self):
#         return self.q.get()
#
# class UserIO:
#     def __init__(self):
#         self.blockingObjects : list[BlockingObject] = []
#
#     def loop(self):
#         while True:
#             user_input = input('Write something')
#             self.blockingObjects[-1].write(user_input)
#             del self.blockingObjects[-1]
#
#     def echo_output(self,the_id: str):
#         the_thing = self.get_input()
#         print(f'Process {the_id} got: {the_thing}')
#
#     def get_input(self):
#         input_retriever = BlockingObject()
#         self.blockingObjects.append(input_retriever)
#         return input_retriever.read()
#
#
# def start_in_thread(funct):
#     threading.Thread(target=funct).start()
#
#
# user_io = UserIO()
# start_in_thread(user_io.loop)
# start_in_thread(lambda: user_io.echo_output(the_id='1'))
# start_in_thread(lambda: user_io.echo_output(the_id='two'))


class UserIO:

    @staticmethod
    def get_user_msg(prompt_msg : str = '') -> str:
        return input(prompt_msg)


    @staticmethod
    def get_confirmation(msg : str) -> bool:
        while True:
            user_input = input(f'{msg}')
            if user_input.lower() in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter (y/n)")


        if user_input == 'y':
            return True
        else:
            return False

# TODO: This object could be accessed from multiple threads so it should be made thread secure
# For example currently if get_user_msg is called from a side thread while it it is called and hasnt return in the main thread
# The main thread will still hold the IO stream and the second call will have to wait until that is done to get it
user_io = UserIO()