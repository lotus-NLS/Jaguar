from dash import Dash
from typing import Optional

from UI.element_types import Layout, ElemAttribute
from UI.chat_page.page_elements.chat_elements import userInput, btn, bottom_container, chat_window

# ----------------------------------------------
# Logic

app = Dash(__name__)

# Layout
the_layout = Layout(element_list=[chat_window, bottom_container])
app.layout = the_layout.get_div_repr()


def make_callback(target_attr : ElemAttribute,
                  trigger_attributes : list[ElemAttribute],
                  funct : callable,
                  state_attributes : Optional[list[ElemAttribute]] = None):

    target = target_attr.make_output()
    triggers = [attr.make_input() for attr in trigger_attributes]
    if not state_attributes is None:
        states = [attr.make_state() for attr in state_attributes]
    else:
        states = []
    return app.callback(target, triggers, states)(funct)




# ----------------------------------------------
# Define callbacks

send_triggers = [btn.n_clicks, userInput.n_submit]

# def get_sent_text_div(n_clicks, n_submit, value):
#     if n_clicks is None and n_submit is None:
#         return []
#     else:
#         return html.Div([
#             html.P(f"User: {value}")
#             ]
#         )

# update_chat_on_send = make_callback(
#     target_attr=chat_window.children,
#     trigger_attributes=send_triggers,
#     state_attributes= [userInput.value],
#     funct=get_sent_text_div
# )

reset_input_on_send = make_callback(
    target_attr=userInput.value,
    trigger_attributes=send_triggers,
    funct = lambda *args: ""
)


if __name__ == '__main__':
    app.run_server(debug=True)
