from typing import Optional
from src.l2_lotus_core import Agent
from src.l2_lotus_core import BaseTool


class Tool(BaseTool):

    def __init__(self):
        super().__init__()
        self.acting_agent: Optional[Agent] = None
        

