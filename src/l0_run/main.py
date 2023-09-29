import time
from typing import Optional, Callable
import types

import inspect


from src.l0_run.entities import DefaultAgent, User
from src.l0_run.gui_element import ChatGUI
from src.l2_lotus_core import Channel, ConversationParticipant,SettingsController

# ---------------------------------------------------------

start_time = time.time()
def log_time_after_done(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"""[Debug]: Completed "{get_fully_qualified_name(func)}"; Uptime: {elapsed_time:.2f} seconds""")

    return wrapper

def get_fully_qualified_name(func):
    try:
        return func.__qualname__
    except:
        return f"{func.__name__}"


class Engine:

    @log_time_after_done
    def __init__(self, enable_introduction = True):
        self.user_channel : Channel = Channel()
        self.user : ConversationParticipant = User()
        self.bots : list[DefaultAgent] = [DefaultAgent()]
        self.settings_controller : Optional[SettingsController] = None

        # TODO: This should be a setting
        self.introduction_enabled: bool = enable_introduction

        ConversationParticipant.enter_into_channel(channel=self.user_channel, participant_list=[self.user] + self.bots)

    @log_time_after_done
    def initialize_settings(self, perform_validation : bool = True) -> None:
        if self.settings_controller is None:
            self.settings_controller = SettingsController()
            self.settings_controller.setup(perform_validation=perform_validation)

    @log_time_after_done
    def start(self, run_in_terminal : bool = True):
        print(f'[Debug]: Lotus started')

        if self.introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if run_in_terminal:
            while True:
                self.user.speak(input(''))
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
    the_engine.start(run_in_terminal=True)

if __name__ == "__main__":
    main()

