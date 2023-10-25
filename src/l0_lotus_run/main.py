from typing import Optional
from pyutils import DevLogger
from src.l3_lotus_core import Channel, LingualEntity,SettingsController, user_io, get_setting
from src.l3_lotus_core import DialogueSettings, Flag
from src.l2_lotus_agent import Agent

from src.l0_lotus_run.entities import Alpha, User
from src.l0_lotus_run.parse_input import get_parsed_input
# ---------------------------------------------------------

class Engine:
    def __init__(self):
        self.user_channel : Optional[Channel] = None
        self.user : Optional[LingualEntity] = None
        self.bots : Optional[list[Agent]] = None
        self.settings_controller : Optional[SettingsController] = None


    def initialize_entities(self):
        self.user = User()
        self.bots = [Alpha()]


    @staticmethod
    def initialize_IO():
        user_io.launch()

    def initialize_communications(self):
        self.user_channel = Channel()
        for participant in [self.user]+self.bots:
            participant.join_channel(self.user_channel)

    def initialize_settings(self, perform_validation : bool = True):
        if self.settings_controller is None:
            self.settings_controller = SettingsController()
            self.settings_controller.setup(perform_validation=perform_validation)

    def run(self):
        print(f'[Debug]: Lotus started')
        if get_setting(DialogueSettings.enable_introduction_label):
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        while True:
            user_input = user_io.get_user_msg()
            msg, flags = get_parsed_input(user_input)
            if Flag.get_quit_flag() in flags:

                break

            if Flag.get_reset_flag() in flags:
                [bot.clear_log() for bot in self.bots]
                print(f'[Debug]: Bot logs cleared')
                continue

            print(f'[Debug]: Flags are {flags}')
            self.user.speak(msg=msg, flags=flags)

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

