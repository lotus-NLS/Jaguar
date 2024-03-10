from hollarek.logging import Loggable
from engine.l5_singletons import Settings, EngineIO
from .entities import ConsoleUser
from engine.l1_agent import Agent
# ---------------------------------------------------------


class LotusEngine(Loggable):
    def __init__(self, use_local : bool = True):
        super().__init__()

        self.settings : Settings = Settings(local=use_local, validate=True)
        self.handler: Agent = Agent()
        self.io: EngineIO = EngineIO(handler=self.handler)


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
            for text in response.primary_stream:
                print(text, end='')



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