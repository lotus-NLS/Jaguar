import time

from holytools.logging import Loggable
from engine.l5_settings import LotusSettings
from engine.l1_agent import Agent
from .dev_user import DevUser
from .server import Server, DevServer
# ---------------------------------------------------------


class LotusEngine(Loggable):
    def __init__(self, use_local : bool = True):
        super().__init__()
        LotusSettings.set_configs(use_local=use_local, enable_validation=True)
        self.handler: Agent = Agent()
        self.engine_io: Server = DevServer(handler=self.handler)


    def launch(self, on_console : bool):
        self.log(f'Lotus started')
        self.engine_io.run()
        if on_console:
            self._launch_console()
        else:
            raise NotImplementedError('Webapp not yet implemented')
        self.stop()


    def _launch_console(self):
        dev_user = DevUser(engineIO=self.engine_io)
        while True:
            user_input = input(f'\nUser: ')
            if user_input == 'exit':
                break
            dev_user.add_input(msg=user_input)
            response = dev_user.fire()
            print(f'GOTO: ', end='')
            for text in response.iter_content(chunk_size=None, decode_unicode=True):
                print(text, end='', flush=True)
                time.sleep(0.05)

    def stop(self):
        self.log(f'Lotus stopped')
        self.engine_io.kill()

