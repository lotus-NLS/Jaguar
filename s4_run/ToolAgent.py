from s2_agent.Agent import Agent
from s2_agent.Tool import Tool


class ToolAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_tools(tool_classes=Tool.all_tools)