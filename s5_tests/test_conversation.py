import time

from s1_conversation.Conversation import Conversation, ConversationParticipant, Dialogue_Roles
from s5_tests.TestModule import TestModule



class conversation_test_module(TestModule):

    class Rowdy_participant(ConversationParticipant):
        def _reaction_protocol(self, dialogue_line: dict):
            role = dialogue_line['role']
            if role == Dialogue_Roles.agent:
                self.speak('Actually, leave me alone! Let me talk to another user')

            if role == Dialogue_Roles.user:
                self.speak('Hello, how can I assist you today')

    def __init__(self):
        super().__init__()
        self.conversation = Conversation()

        # Create participants and add them to the handler
        self.agent_participant1 = ConversationParticipant(role=Dialogue_Roles.agent)
        self.agent_participant2 = ConversationParticipant(role=Dialogue_Roles.agent)
        self.agent_participant3 = ConversationParticipant(role=Dialogue_Roles.agent)

        self.rowdy_user_participant = conversation_test_module.Rowdy_participant(role=Dialogue_Roles.user)
        self.agent_participants = [self.agent_participant1, self.agent_participant2, self.agent_participant3, self.rowdy_user_participant]

        for particpant in self.agent_participants:
            particpant.join_conversation(self.conversation)

    # Expects output:
    # assistant said: Hello from participant 1!
    # assistant said: Hello from participant 2!
    # assistant thought: I do not even want to say hello to that guy!
    # Logs for Participant1:
    # [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}]
    # Logs for Participant2:
    # [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}, {'role': 'assistant', 'content': 'I do not even want to say hello to that guy!'}]
    def test_speak_and_think(self):
        self.agent_participant1.speak('Hello from participant 1!')
        self.agent_participant2.speak('Hello from participant 2!')
        self.agent_participant2.think('I do not even want to say hello to that guy!')

        time.sleep(0.5)
        print("Logs for Participant1:")
        self.agent_participant1.print_memory()

        print("Logs for Participant2:")
        self.agent_participant2.print_memory()

        print("Logs for Participant2:")
        self.agent_participant3.print_memory()


    def test_reaction(self):
        self.rowdy_user_participant.join_conversation(self.conversation)
        self.agent_participant1.speak('How are you :)')

        time.sleep(1)
        # Participants print their logs
        print("Logs for Participant1:")
        self.agent_participant2.print_memory()

        print("Logs for Participant2:")
        self.agent_participant3.print_memory()

        # test_reaction()



# if __name__ == "__main__":
#     speak_and_think()


# ----------------------------------------------------
# Test driver code


# Since rowdy_participant is itself an agent this will trigger infinite recursion

def test_reaction():
