import time
from typing import Optional
from pyutils import DevLogger, CustomThread
from pywebdev import PyWebApp
from engine.l2_agent.m1_language import Channel, LingualEntity
from engine.l3_singletons import LotusSettings, DialogueSettings
from engine.l2_agent import Agent

from engine.l3_singletons.m0_server.engine_io import EngineIO
from engine.l0_main.entities import Alpha, User
# ---------------------------------------------------------

class LotusEngine:

    @DevLogger.logging_wrapper
    def __init__(self, web_app : PyWebApp):
        self.user_channel : Channel = Channel()
        self.user : LingualEntity = User()
        self.settings : LotusSettings = LotusSettings()
        self.IO : EngineIO = EngineIO(web_app=web_app)

        self.bots: Optional[list[Agent]] = None

    @DevLogger.logging_wrapper
    def initialize_agents(self):
        self.bots = [Alpha()]

    @DevLogger.logging_wrapper
    def launch_communications(self):
        for participant in [self.user]+self.bots:
            self.user_channel.add_entity(entity=participant)

    @DevLogger.logging_wrapper
    def setup_settings(self, perform_validation : bool = True):
        self.settings.setup(perform_validation=perform_validation)

    @DevLogger.logging_wrapper
    def run(self):
        self.initialize_agents()
        self.launch_communications()
        self.setup_settings(perform_validation=True)
        print(f'[Debug]: Lotus started')

        if DialogueSettings().get_enable_introduction():
           self.user.enqueue('[Manual inquiry for user]: Who are you and what can you do?')

        while True:
            user_entry = EngineIO().get_user_entry()
            flags = user_entry.get_flags()
            print(f'[Debug]: The user said {user_entry.get_content()}')
            print(f'[Debug]: Flags are {flags}')
            flags.is_entry_end = True

            if flags.print_threads:
                CustomThread.print_active_customthreads()
                continue

            if flags.quit:
                break

            if flags.reset:
                [bot.clear_log() for bot in self.bots]
                print(f'[Debug]: Bot logs cleared')
                continue

            self.user.enqueue(msg=user_entry.get_content(), flags=flags)

