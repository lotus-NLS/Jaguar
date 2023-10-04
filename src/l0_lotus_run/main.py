import time
from typing import Optional
from src.l3_lotus_core import Channel, LingualEntity,SettingsController, log_time_after_done


from src.l0_lotus_run.entities import Alpha, User
from src.l0_lotus_run.gui_element import ChatGUI
from src.l0_lotus_run.parse_input import get_parsed_input
# ---------------------------------------------------------

class Engine:
    @log_time_after_done
    def __init__(self, enable_introduction = True):
        self.user_channel : Channel = Channel()
        self.user : LingualEntity = User()
        self.bots : list[Alpha] = [Alpha()]
        self.settings_controller : Optional[SettingsController] = None

        # TODO: This should be a setting
        self.introduction_enabled: bool = enable_introduction

        LingualEntity.enter_into_channel(channel=self.user_channel, channel_members=[self.user] + self.bots)

    @log_time_after_done
    def initialize_settings(self, perform_validation : bool = True):
        if self.settings_controller is None:
            self.settings_controller = SettingsController()
            self.settings_controller.setup(perform_validation=perform_validation)

    @log_time_after_done
    def run(self, run_in_terminal : bool = True):
        print(f'[Debug]: Lotus started')

        if self.introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if run_in_terminal:
            while True:
                user_input = input('')
                msg, flags = get_parsed_input(user_input)
                print(f'[Temp debug]: Flags are {flags}')
                self.user.speak(msg=msg, flags=flags)
                time.sleep(0.5)

        else:
            gui = ChatGUI(send_callback=self.user.speak, channel=self.user_channel)
            gui.run()



def main():
    # Initialize user, agents and conversation hub
    the_engine : Engine = Engine(enable_introduction=False)

    # Read or write settings if no settings available
    the_engine.initialize_settings(perform_validation=True)

    # Start the routine
    the_engine.run(run_in_terminal=True)

if __name__ == "__main__":
    main()

