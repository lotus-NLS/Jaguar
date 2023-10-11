from typing import Optional
from src.l3_lotus_core import log_engine_step, Channel, LingualEntity,SettingsController, user_io, get_setting
from src.l3_lotus_core import DialogueSettings
from src.l2_lotus_agent import Agent


from src.l0_lotus_run.entities import Alpha, User
from src.l0_lotus_run.gui_element import ChatGUI
from src.l0_lotus_run.parse_input import get_parsed_input
# ---------------------------------------------------------

class Engine:
    @log_engine_step
    def __init__(self):
        self.user_channel : Optional[Channel] = None
        self.user : Optional[LingualEntity] = None
        self.bots : Optional[list[Agent]] = None
        self.settings_controller : Optional[SettingsController] = None


    @log_engine_step
    def initialize_entities(self):
        self.user = User()
        self.bots = [Alpha()]

    @log_engine_step
    def initialize_communications(self):
        self.user_channel = Channel()
        LingualEntity.enter_into_channel(channel=self.user_channel, channel_members=[self.user] + self.bots)

    @log_engine_step
    def initialize_settings(self, perform_validation : bool = True):
        if self.settings_controller is None:
            self.settings_controller = SettingsController()
            self.settings_controller.setup(perform_validation=perform_validation)

    @log_engine_step
    def run(self, run_in_terminal : bool = True):
        print(f'[Debug]: Lotus started')

        if get_setting(DialogueSettings.enable_introduction_label):
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if run_in_terminal:
            while True:
                user_input = user_io.get_user_msg()
                msg, flags = get_parsed_input(user_input)
                print(f'[Debug]: Flags are {flags}')
                self.user.speak(msg=msg, flags=flags)

        else:
            gui = ChatGUI(send_callback=self.user.speak, channel=self.user_channel)
            gui.run()




def main():
    # Initialize the engine as empty vessel
    the_engine : Engine = Engine()

    # Initialize user and agents
    the_engine.initialize_entities()

    # Initialize communication hub
    the_engine.initialize_communications()

    # Read or write settings if no settings available
    the_engine.initialize_settings(perform_validation=True)

    # Start the routine
    the_engine.run(run_in_terminal=True)

if __name__ == "__main__":
    main()

