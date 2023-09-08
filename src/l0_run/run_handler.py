import time

from src.l0_run.entities import DefaultAgent, User
from src.l0_run.gui_element import ChatGUI
from src.l2_lotus_core import Channel, ConversationParticipant,SettingsController

# ---------------------------------------------------------

class RunModes:
    gui = 0
    command_line = 1


class Engine:
    def __init__(self, mode = RunModes.command_line, is_introduction_enabled = True):
        self.mode : int = mode
        self.user_channel = Channel()
        self.user : ConversationParticipant = User()
        self.bots : list[ConversationParticipant] = [DefaultAgent()]

        self.gui : ChatGUI = ChatGUI(send_callback=self.user.speak, channel=self.user_channel)

        ConversationParticipant.enter_into_conversation(channel=self.user_channel, participant_list=[self.user] + self.bots)
        self.is_introduction_enabled : bool = is_introduction_enabled


    def start(self):
        print(f'[Debug]: Lotus started')

        if self.is_introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if self.mode == RunModes.command_line:
            while True:
                self.user.speak(input(''))
                time.sleep(0.5)
                print(f'[Debug]: Current conversation memory of the bot: {self.bots[0].get_memory()}')

        else:
            self.gui.run()

def main():
    settings_controller = SettingsController()
    settings_controller.setup()

    this_run_handler = Engine(is_introduction_enabled=False, mode=RunModes.gui)
    this_run_handler.start()

if __name__ == "__main__":
    main()

