# import logging
# from typing import Optional
# from pyutils import CustomThread
# from api import Flag
#
# from engine.l1_agent.m1_language import Channel, LingualEntity
# from engine.l1_agent import Agent
# from engine.l3_singletons.io.io import EngineIO

from hollarek.tmpl import Loggable
from engine.l0_main.entities import Alpha, User
from engine.l4_singletons import LotusSettings
# ---------------------------------------------------------

class LotusEngine(Loggable):

    def __init__(self, ip : str, port : int, local : bool = False):
        super().__init__()
        self.settings : LotusSettings = LotusSettings(local=local, validate=True)

        self.user : LingualEntity = User()
        self.IO : EngineIO = EngineIO(ip,port)
        self.bots: Optional[list[Agent]] = None


    def initialize_agents(self):
        self.bots = [Alpha()]


    def launch_entity_communication(self):
        for participant in [self.user]+self.bots:
            self.user_channel.add_entity(entity=participant)


    def launch_IO(self):
        self.IO.launch()


    def run(self):
        self.initialize_agents()
        self.launch_entity_communication()
        self.launch_IO()

        self.log(f'Lotus started')

        if LotusSettings.get_enable_introduction():
            self.user.enqueue('[Manual inquiry for user]: Who are you and what can you do?',final=True)

        while True:
            user_entry = EngineIO().get_response_stream()
            flags = user_entry.get_flags()
            logging.info(f'The user said {user_entry.get_content()}')
            # print(f'[Debug]: Flags are {flags.()}')

            if flags._get(flag=Flag.PRINT_THREADS):
                CustomThread.print_active_customthreads()
                continue

            if flags._get(flag=Flag.QUIT):
                break

            if flags._get(flag=Flag.RESET):
                [bot.clear_log() for bot in self.bots]
                logging.info(f'Bot logs cleared')
                continue

            self.user.enqueue(msg=user_entry.get_content(), final=True)
