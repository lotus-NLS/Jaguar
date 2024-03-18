import os
import threading
import time

from pynput.keyboard import Key
from hollarek.core.logging import Loggable
from hollarek.hardware import KeyboardListener
from engine.l5_singletons import LotusSettings, EngineIO
from engine.l1_agent import Agent
from .entities import DevUser
# ---------------------------------------------------------


class LotusEngine(Loggable):
    def __init__(self, use_local : bool = True):
        super().__init__()

        self.settings : LotusSettings = LotusSettings(use_local=use_local, validate=True)
        self.handler: Agent = Agent()
        self.engine_io: EngineIO = EngineIO(handler=self.handler)
        threading.Thread(target=self.stop_on_esc, daemon=True).start()


    def launch(self, on_console : bool):
        self.log(f'Lotus started')
        self.engine_io.dev_run()
        if on_console:
            self._launch_console()
        else:
            raise NotImplementedError('Webapp not yet implemented')
        self.stop()


    def _launch_console(self):
        dev_user = DevUser(engineIO=self.engine_io)
        while True:
            user_input = input()
            if user_input == 'exit':
                break
            dev_user.add_input(msg=user_input)
            response = dev_user.fire()
            for text in response.iter_content(chunk_size=None, decode_unicode=True):
                print(text, end='', flush=True)
                time.sleep(0.05)


    def stop_on_esc(self):
        KeyboardListener().wait_on_hold(key=Key.esc, duration=2)
        self.stop()

    # noinspection PyProtectedMember
    def stop(self):
        self.log(f'Lotus stopped')
        self.engine_io.dev_kill()
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