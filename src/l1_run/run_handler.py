import time

from src.l1_run.entities import DefaultAgent,GUI_User, User
from src.l1_run.setup import setup
from src.l5_conversation.l0_conversation_participant import Channel, ConversationParticipant

# ---------------------------------------------------------


class RunModes:
    gui = 0
    command_line = 1


class RunHandler:
    def __init__(self, mode = RunModes.command_line, is_introduction_enabled = True):
        self.mode : int = mode
        self.user : ConversationParticipant = User() if self.mode == RunModes.command_line else GUI_User()
        self.bots : list[ConversationParticipant] = [DefaultAgent()]
        self.channel = Channel()

        ConversationParticipant.enter_into_conversation(channel=self.channel, participant_list=[self.user] + self.bots)
        self.is_introduction_enabled : bool = is_introduction_enabled

    def start(self):
        print(f'[Debug]: Lotus started')

        if self.is_introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if self.mode == RunModes.command_line:
            while True:
                self.user.speak(input(''))
                time.sleep(0.5)
                # print(f'[Debug]: Current conversation memory of the bot: {self.bots[0].get_memory()}')

        else:
            self.user : GUI_User
            self.user.window.mainloop()

def main():
    setup()
    this_run_handler = RunHandler(is_introduction_enabled=False)
    this_run_handler.start()

if __name__ == "__main__":
    main()

