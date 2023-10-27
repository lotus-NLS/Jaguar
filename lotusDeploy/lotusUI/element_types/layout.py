from typing import List, Optional
from .element import Element
from dash import html

class Layout:
    def __init__(self, element_list : List[Element], script_list : Optional[list] = None):
        self.element_list = element_list
        self.script_list = script_list

    def get_div_repr(self):
        children = [elem.component for elem in self.element_list]
        if not self.script_list is None:
            children += self.script_list

        return html.Div(children=children)
