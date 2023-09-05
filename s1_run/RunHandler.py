

import time
from s1_run.Entities import DefaultAgent,GUI_User, User
from s4_conversation.s0_ConversationParticipant import Channel, enter_into_conversation, ConversationParticipant
from s1_run.setup import setup

class RunModes:
    gui = 0
    command_line = 1



class RunHandler:
    def __init__(self, mode = RunModes.command_line, is_introduction_enabled = True):
        self.mode : int = mode
        self.user : ConversationParticipant = User() if self.mode == RunModes.command_line else GUI_User()
        self.bots : list[ConversationParticipant] = [DefaultAgent()]
        self.channel = Channel()

        enter_into_conversation(channel=self.channel, participant_list=[self.user] + self.bots)
        self.is_introduction_enabled : bool = is_introduction_enabled
        self.start()

    def start(self):
        if self.is_introduction_enabled:
           self.user.speak('[Manual inquiry for user]: Who are you and what can you do?')

        if self.mode == RunModes.command_line:
            # self.user.speak('Run hello world for me')
            while True:
                self.user.speak(input(''))
                time.sleep(0.5)
                print(f'[Debug]: Current conversation memory of the bot: {self.bots[0].get_memory()}')

        else:
            self.user : GUI_User
            self.user.window.mainloop()

def main():
    setup()
    this_run_handler = RunHandler(is_introduction_enabled=False)
    this_run_handler.start()

if __name__ == "__main__":
    main()

