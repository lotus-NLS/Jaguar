from typing import Optional

from PIL.Image import Image as PILImage
from engine.l2_os.application import Tab
from hollarek.hardware import TextMouse, Keyboard, Display, Grid

# ---------------------------------------------------

class HostTab(Tab):
    def __init__(self, uri : str):
        super().__init__(uri=uri)
        self.input_grid = Grid(20,20)
        self.text_mouse = TextMouse(input_grid=self.input_grid)
        self.keyboard = Keyboard()

    def get_text(self) -> str:
        return ''

    def get_image(self) -> Optional[PILImage]:
        display = Display.get_primary()
        display.get_screenshot(grid=self.input_grid)

    def click(self, x : int, y : int):
        self.text_mouse.click(x, y)

    def type(self, msg : str):
        self.keyboard.type(msg=msg)

