from typing import Optional
from src.l2_lotus_agent import Agent, BaseTool

# Generic tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [Update] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any
# ---------------------------------------------------------


class Tool(BaseTool):
    def __init__(self):
        super().__init__()
        self.acting_agent: Optional[Agent] = None
        

