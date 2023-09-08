from src.l2_lotus_core import Agent, ConversationParticipant, DialogueRole
from src.l1_lotus_tools import RUN,READ,WRITE,BROWSE

# ---------------------------------------------------------

class DefaultAgent(Agent):
    def __init__(self):
        super().__init__()
        self.set_tools(tool_types=[READ, WRITE, RUN, BROWSE])


class User(ConversationParticipant):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user())


