from src.l2_lotus_core import Agent, ConversationParticipant, DialogueRole
from src.l1_lotus_tools import RUN,READ,WRITE,SEARCH

# ---------------------------------------------------------

class DefaultAgent(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools(tool_types=[READ, WRITE, RUN, SEARCH])


class User(ConversationParticipant):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user())


