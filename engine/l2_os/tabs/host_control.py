from typing import Optional

from PIL.Image import Image as PILImage
from engine.l2_os.application import Workspace
from hollarek.hardware import TextMouse, Keyboard, Display, Grid

# ---------------------------------------------------

class Host(Workspace):
    def __init__(self, uri : str):
        super().__init__(uri=uri)
        self.input_grid = Grid(20,20)
        self.text_mouse = TextMouse(input_grid=self.input_grid)
        self.keyboard = Keyboard()
        self.display = Display.get_primary()

    def get_text(self) -> str:
        return ''

    def get_image(self) -> Optional[PILImage]:
        return self.display.get_screenshot(grid=self.input_grid)

    def click(self, cell_num : int):
        self.text_mouse.click(cell_num=cell_num, on_primary_display=self.display.is_primary)

    def type(self, msg : str):
        self.keyboard.type(msg=msg)


