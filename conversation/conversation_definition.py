from participant import Conversation_Participant


class Conversation:
    def __init__(self):
        self._participants = []

    def add_participant(self, participant):
        self._participants.append(participant)

    def broadcast_message(self, role, msg):
        print(f'{role} sent a message: {msg}')

        for participant in self._participants:
            participant : Conversation_Participant
            participant.conversational_memory.append({"role": role, "content": msg})