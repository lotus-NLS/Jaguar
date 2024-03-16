import os
import threading
import time

from pynput.keyboard import Key
from hollarek.logging import Loggable
from hollarek.hardware import KeyboardListener
from engine.l5_singletons import Settings, IO
from .entities import ConsoleUser
from engine.l1_agent import Agent
# ---------------------------------------------------------


class LotusEngine(Loggable):
    def __init__(self, use_local : bool = True):
        super().__init__()

        self.settings : Settings = Settings(local=use_local, validate=True)
        self.handler: Agent = Agent()
        self.io: IO = IO(handler=self.handler)
        threading.Thread(target=self.stop_on_esc, daemon=True).start()

    def launch(self, on_console : bool):
        self.log(f'Lotus started')
        if on_console:
            self._launch_console()
        else:
            raise NotImplementedError('Webapp not yet implemented')



    @staticmethod
    def _launch_console():
        user = ConsoleUser()
        while True:
            user_input = input()
            if user_input == 'exit':
                break
            response = user.send(msg=user_input)
            for text in response.get_text_stream():
                print(text, end='', flush=True)
                time.sleep(0.05)

    # noinspection PyProtectedMember
    def stop_on_esc(self):
        KeyboardListener().wait_on_hold(key=Key.esc, duration=2)
        self.log(f'Lotus stopped')
        os._exit(0)


        # listener.wait_on_hold(key=)

            # if flags.get(flag=Flag.PRINT_THREADS):
            #     CustomThread.print_active_customthreads()
            #     continue
            #
            # if flags.get(flag=Flag.QUIT):
            #     break
            #
            # if flags.get(flag=Flag.RESET):
            #     [bot.clear_log() for bot in self.handler]
            #     logging.info(f'Bot logs cleared')
            #     continue
            #
            # self.user.enqueue(msg=user_entry.get_content(), final=True)