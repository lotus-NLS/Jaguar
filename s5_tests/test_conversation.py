import time

from s1_conversation.Conversation import Conversation, ConversationParticipant, Dialogue_Roles


def test_speak_and_think():

    # Create participants and add them to the handler
    participant1 = ConversationParticipant(role=Dialogue_Roles.agent)
    participant2 = ConversationParticipant(role=Dialogue_Roles.agent)
    participant3 = ConversationParticipant(role=Dialogue_Roles.agent)

    this_conversation = Conversation(participant_list=[participant1,participant2,participant3])

    # Participants write messages
    participant1.speak('Hello from participant 1!')
    participant2.speak('Hello from participant 2!')

    participant2.think('I do not even want to say hello to that guy!')

    # Participants print their logs
    time.sleep(0.5)
    print("Logs for Participant1:")
    participant1.print_memory()

    print("Logs for Participant2:")
    participant2.print_memory()

    print("Logs for Participant2:")
    participant3.print_memory()


# Expects output:
# assistant said: Hello from participant 1!
# assistant said: Hello from participant 2!
# assistant thought: I do not even want to say hello to that guy!
# Logs for Participant1:
# [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}]
# Logs for Participant2:
# [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}, {'role': 'assistant', 'content': 'I do not even want to say hello to that guy!'}]

# if __name__ == "__main__":
#     speak_and_think()


# ----------------------------------------------------
# Test driver code


# Since rowdy_participant is itself an agent this will trigger infinite recursion

def test_reaction():
    class Rowdy_participant(ConversationParticipant):

        def _reaction_protocol(self, dialogue_line : dict):
            role = dialogue_line['role']
            if role == Dialogue_Roles.agent:
                self.speak('Actually, leave me alone! Let me talk to the user')

            if role == Dialogue_Roles.user:
                self.speak('Hello, how can I assist you today')


    participant1 = ConversationParticipant(role=Dialogue_Roles.agent)
    participant2 = ConversationParticipant(role=Dialogue_Roles.agent)
    participant3 = Rowdy_participant(Dialogue_Roles.agent)

    this_conversation = Conversation(participant_list=[participant1,participant2,participant3])

    participant1.speak('How are you :)')

    time.sleep(1)
    # Participants print their logs
    print("Logs for Participant1:")
    participant1.print_memory()

    print("Logs for Participant2:")
    participant2.print_memory()

# test_reaction()
test_speak_and_think()