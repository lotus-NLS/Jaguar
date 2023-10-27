from dash import dcc
from typing import Union, List, Dict, Any
from typing import Optional
from dash import  html, Input, Output, State


# ----------------------------------------------


class ElemAttribute:
    def __init__(self,label : str, parent_elem ):
        self.parent_elem = parent_elem
        self.label = label
        self.val = None

    def get_parent_id(self) -> str:
        return self.parent_elem.get_id()

    def make_input(self):
        return Input(self.get_parent_id(),self.label)

    def make_output(self):
        return Output(self.get_parent_id(), self.label)

    def make_state(self):
        return State(self.get_parent_id(), self.label)



class Element:
    def __init__(self, component, elem_id):
        super().__init__()
        self.component = component
        self.id  = elem_id

    def get_id(self) -> Optional[str]:
        return self.id

    def add_attribute(self, label : str):
        attr = ElemAttribute(label=label, parent_elem=self)
        return attr


class DivElem(Element):
    def __init__(self,
                 div_id: str,
                 children: Union[str, List[Any]] = None,
                 style: Dict[str, Any] = None,
                 **kwargs):
        super().__init__(component=html.Div(children=children, id=div_id, style=style, **kwargs),
                         elem_id=div_id)
        self.children = self.add_attribute(label='children')
        self.n_clicks = self.add_attribute(label='n_clicks')



class InputElem(Element):
    def __init__(self,
                 the_id: str,
                 value: str  = '',
                 input_type: str = "text",
                 placeholder: str = None,
                 style: Dict[str, Any] = None,
                 **kwargs):
        the_component = dcc.Input(id=the_id,
                                  autoComplete='off',
                                  value=value,
                                  type=input_type,
                                  placeholder=placeholder,
                                  style=style,
                                  **kwargs)
        super().__init__(component=the_component,
                         elem_id=the_id)
        self.n_submit = self.add_attribute(label='n_submit')
        self.value = self.add_attribute(label='value')

    def get_value(self):
        return self.component.value
