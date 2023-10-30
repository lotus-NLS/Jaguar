from .colors import Color
from .cursors import Cursor
from .sizes import Pixels, Percentage
from .position import Position

class Style(dict):
    def __init__(self,

                 width: (Pixels, Percentage) = None,
                 height: (Pixels, Percentage) = None,
                 background_color: Color = None,
                 border: str = None,
                 position: Position = None,
                 padding: (Pixels, Percentage) = None,
                 margin: (Pixels, Percentage) = None,
                 color: Color = None,
                 cursor: Cursor = None,
                 transition: str = None,
                 **other_styles):

        super().__init__()

        if width:
            self["width"] = width
        if height:
            self["height"] = height
        if background_color:
            self["backgroundColor"] = background_color
        if border:
            self["border"] = border
        if padding:
            self["padding"] = padding
        if margin:
            self["margin"] = margin
        if color:
            self["color"] = color
        if cursor:
            self["cursor"] = cursor
        if transition:
            self["transition"] = transition
        if position:
            self['position'] = position

        self.update(other_styles)

    def __str__(self):
        return "; ".join(f"{key}: {value}" for key, value in self.items())