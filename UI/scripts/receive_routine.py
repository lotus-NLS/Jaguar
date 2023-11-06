from pywebdev.browser import window, document

# ----------------------------------------------

# socket = window.io.connect('http://localhost:5000')
# chat_window = document["chat-window"]
#
# def make_new_entry(msg):
#     new_element = document.createElement("div")
#     new_element.innerHTML = f"<p>Agent: {msg}</p>"
#     chat_window.appendChild(new_element)
#
# def handle_agent_msg(msg : str, is_new_entry = False):
#     window.console.log('Agent message arrived :)')
#
#     last_element = chat_window.children[-1] if len(chat_window.children) > 0 else None
#
#     if is_new_entry or last_element is None:
#         make_new_entry(msg=msg)
#     else:
#         last_element.innerHTML = f"<p>{msg}</p>"
#
# socket.on('agentmessage', handle_agent_msg)
