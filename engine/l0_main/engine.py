from hollarek.logging import Loggable
from engine.l5_singletons import Settings, EngineIO
from .entities import ConsoleUser, User
from engine.l1_agent import Agent
# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self, local : bool = True, on_console : bool = True):
        super().__init__()
        self.settings : Settings = Settings(local=local, validate=True)


        self.handler: Agent = Agent()
        self.io: EngineIO = EngineIO(handler=self.handler)
        self.launch(on_console)

    def launch(self, on_console : bool):
        self.log(f'Lotus started')
        if on_console:
            self.launch_console()
        else:
            raise NotImplementedError('Webapp not yet implemented')


    @staticmethod
    def launch_console():
        user = ConsoleUser()
        while True:
            user_input = input()
            if user_input == 'exit':
                break
            user.send(msg=user_input)


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
