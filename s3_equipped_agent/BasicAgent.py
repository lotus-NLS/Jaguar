from s2_agent.Agent import Agent
from Toolbox import  Toolbox,basic_tools


class BasicAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_tool_list(basic_tools)