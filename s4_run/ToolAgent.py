from s2_agent.Agent import Agent
from s3_toolbox.FileIO import READ,WRITE
from s3_toolbox.Run import RUN

class ToolAgent(Agent):
    def __init__(self):
        super().__init__()
        self.add_tools(tool_classes=[READ,WRITE,RUN])