import time

from src.l0_run.entities import DefaultAgent, User
from src.l0_run.gui_element import ChatGUI
from src.l2_lotus_core import Channel, ConversationParticipant,SettingsController

# ---------------------------------------------------------

class RunModes:
    gui = 0
    command_line = 1


class Engine:
    def __init__(self, enable_introduction = True):
        self.user_channel : Channel = Channel()
        self.user : ConversationParticipant = User()
        self.bots : list[DefaultAgent] = [DefaultAgent()]

        ConversationParticipant.enter_into_conversation(channel=self.user_channel, participant_list=[self.user] + self.bots)
        self.is_introduction_enabled : bool = enable_introduction


    def start(self, mode = RunModes.gui):
        print(f'[Debug]: Lotus started')

        if self.is_introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if mode == RunModes.command_line:
            # TODO : Remove
            self.user.speak('Initialize a test directive')

            while True:
                # self.user.speak(input(''))

                time.sleep(0.5)
                print(f'[Debug]: Current conversation memory of the bot: {self.bots[0].get_text_context()}')

        else:
            gui = ChatGUI(send_callback=self.user.speak, channel=self.user_channel)
            gui.run()


def log_uptime(start_time):
    elapsed_time = time.time() - start_time
    print(f'[Debug]: Uptime: {elapsed_time:.2f} seconds')


def main():
    start_time = time.time()

    settings_controller = SettingsController()
    log_uptime(start_time=start_time)

    settings_controller.setup(perform_validation = True)
    log_uptime(start_time=start_time)

    this_run_handler = Engine(enable_introduction=False)
    log_uptime(start_time=start_time)

    this_run_handler.start(mode=RunModes.command_line)

if __name__ == "__main__":
    main()

