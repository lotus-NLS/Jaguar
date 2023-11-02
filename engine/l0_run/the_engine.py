from typing import Optional
from pyutils import DevLogger, CustomThread
from api import LotusServer
from engine.l2_agent.m1_language import Channel, LingualEntity
from engine.l3_settings import DialogueSettings, SettingsController, get_setting
from engine.l2_agent import Agent

from engine.l0_run.entities import Alpha, User
# ---------------------------------------------------------

class Engine:
    def __init__(self):
        self.user_channel : Optional[Channel] = None
        self.user : Optional[LingualEntity] = None
        self.bots : Optional[list[Agent]] = None
        self.settings_controller : Optional[SettingsController] = None
        self.server : Optional[LotusServer] = None

    def initialize_entities(self):
        self.user = User()
        self.bots = [Alpha()]


    def initialize_IO(self):
        self.server = LotusServer()
        self.server.start()


    def initialize_communications(self):
        self.user_channel = Channel()
        for participant in [self.user]+self.bots:
            self.user_channel.add_entity(entity=participant)


    def initialize_settings(self, perform_validation : bool = True):
        if self.settings_controller is None:
            self.settings_controller = SettingsController()
            self.settings_controller.setup(perform_validation=perform_validation)

    def run(self):
        print(f'[Debug]: Lotus started')
        if get_setting(DialogueSettings.enable_introduction_label):
           self.user.enqueue('[Manual inquiry for user]: Who are you and what can you do?')

        while True:
            user_entry = LotusServer().get_user_entry()
            flags = user_entry.get_flags()
            print(f'[Debug]: The user said {user_entry.get_content()}')
            print(f'[Debug]: Flags are {flags}')

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


    # Make the engine log the individual steps
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if callable(attr):
            attr = DevLogger.logging_wrapper(attr)
        return attr


def main():
    # Initialize the engine as empty vessel
    the_engine : Engine = Engine()

    # Create user and bot entities
    the_engine.initialize_entities()

    # Communicate with LotusDeploy
    the_engine.initialize_IO()

    # Facilitate communications between entities
    the_engine.initialize_communications()

    # Read or write settings if no settings available
    the_engine.initialize_settings(perform_validation=True)

    # Start the routine
    the_engine.run()

if __name__ == "__main__":
    main()

