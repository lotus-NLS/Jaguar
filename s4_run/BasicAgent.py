from s2_agent.Agent import Agent
from s3_toolbox.FileIO import READ,WRITE

basic_tools = [READ(), WRITE()]

class BasicAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_tool_list(basic_tools)