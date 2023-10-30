from dash import Dash

# ----------------------------------------------
# Logic

external_scripts = [
    'https://cdn.jsdelivr.net/npm/brython@3.11/brython.min.js"',
    '/static/my_brython_script.py'
]

app = Dash(__name__, external_scripts=external_scripts)

# Layout


# app.layout = html.Div([
#         # Your Dash components here
#         html.Script(
#             type="text/python",
#             children=[
#                 '''
#                 from browser import console
#                 console.log("Hello, World!")
#                 '''
#             ]
#         ),
#         html.Script("brython()")
#     ]
# )


@app.server.after_request
def after_request_func(response):
    if response.content_type == 'text/html; charset=utf-8':
        response.set_data(
            response.get_data().replace(
                b'</body>',
                b'''<script type="text/python">
                    from browser import console
                    console.log("Hello, Worlddd!")
                   </script>
                   <script>brython()</script>
                   </body>'''
            )
        )
    return response


# the_layout = Layout(element_list=[chat_window, bottom_container], script_list=[hello_world])
# app.layout = the_layout.get_div_repr()

#
# def make_callback(target_attr : ElemAttribute,
#                   trigger_attributes : list[ElemAttribute],
#                   funct : callable,
#                   state_attributes : Optional[list[ElemAttribute]] = None):
#
#     target = target_attr.make_output()
#     triggers = [attr.make_input() for attr in trigger_attributes]
#     if not state_attributes is None:
#         states = [attr.make_state() for attr in state_attributes]
#     else:
#         states = []
#     return app.callback(target, triggers, states)(funct)
#
#
#
#
# # ----------------------------------------------
# # Define callbacks
#
# send_triggers = [btn.n_clicks, userInput.n_submit]
#
# reset_input_on_send = make_callback(
#     target_attr=userInput.value,
#     trigger_attributes=send_triggers,
#     funct = lambda *args: ""
# )


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
