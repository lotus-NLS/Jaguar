from __future__ import annotations
from src.l2_lotus_agent import ToolArg
import pyautogui

from src.l1_lotus_tools.tool import Tool

# ---------------------------------------------------------

class TYPE(Tool):

    def __init__(self):
        super().__init__()
        self.desc = f'Trigger keyboard events that behave as if typed by the user'

        self.content_arg: ToolArg = self.create_arg(name='content', dtype=str,
                                                    desc='What you will type')


    def do(self):
        try:
            to_type = self.content_arg.val
            pyautogui.typewrite(f'{to_type}')
            self.update_log(f'Successfully triggered keyboard events to type specified content')

        except:
            self.exception_log(f'An error occured while trying to simulate keyboard events')
